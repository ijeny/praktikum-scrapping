import re
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import pandas as pd
import os

def bersihkan_teks(teks):
    if teks is None:
        return teks

    # Hapus karakter whitespace berlebih dan newline
    teks = teks.strip()
    teks = " ".join(teks.split())

    # Normalisasi Unicode dan hapus karakter non-printable
    teks = re.sub(r"[\s\u00A0]+", " ", teks)

    return teks


def normalisasi_url(url):
    if url is None:
        return url
    return url.strip()


def export_to_excel(rows, filename=None):
    if filename is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "hasil_cleaning.xlsx")

    if not rows:
        print("⚠️ Tidak ada data untuk diekspor ke Excel.")
        return

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"📦 Data berhasil diekspor ke {filename}")

def ambil_judul_detik():
    url = "https://inet.detik.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Konfigurasi Database
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'port': 3307,
        'password': 'ijeny46',
        'database': 'db_scraping'
    }

    conn = None
    try:
        # Inisialisasi koneksi database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("✅ Terhubung ke database.")

        # Buat tabel hasil_cleaning jika belum ada
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hasil_cleaning (
                id INT AUTO_INCREMENT PRIMARY KEY,
                judul_asli TEXT,
                judul_clean TEXT,
                url_link TEXT,
                url_link_clean TEXT,
                url_gambar TEXT,
                waktu_scraping DATETIME
            )
            """
        )

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Parsing HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # Mencari semua elemen judul berita
            daftar_berita = soup.select('a[class*="ph_newsfeed_d"]')

            if not daftar_berita:
                print("❌ Tidak ditemukan judul berita di halaman.")
            else:
                waktu_sekarang = datetime.now()
                saved_count = 0

                cleaned_rows = []

                for berita in daftar_berita[:25]:  # Ambil 25 berita pertama
                    img_tag = berita.find('img')
                    img_url = img_tag.get('src') if img_tag else None
                    judul_asli = " ".join(berita.text.split())
                    judul_clean = bersihkan_teks(judul_asli)
                    url_link = berita.get('href')
                    url_link_clean = normalisasi_url(url_link)

                    # Simpan data mentah ke tabel tbl_berita
                    sql_raw = "INSERT INTO tbl_berita (judul, url_link, url_gambar, waktu_scraping) VALUES (%s, %s, %s, %s)"
                    val_raw = (judul_asli, url_link, img_url, waktu_sekarang)
                    cursor.execute(sql_raw, val_raw)

                    # Simpan data hasil cleaning ke tabel hasil_cleaning
                    sql_clean = (
                        "INSERT INTO hasil_cleaning (judul_asli, judul_clean, url_link, url_link_clean, url_gambar, waktu_scraping) "
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                    )
                    val_clean = (judul_asli, judul_clean, url_link, url_link_clean, img_url, waktu_sekarang)
                    cursor.execute(sql_clean, val_clean)

                    cleaned_rows.append({
                        'judul_asli': judul_asli,
                        'judul_clean': judul_clean,
                        'url_link': url_link,
                        'url_link_clean': url_link_clean,
                        'url_gambar': img_url,
                        'waktu_scraping': waktu_sekarang,
                    })

                    saved_count += 1
                    print(f"Disimpan: {judul_clean[:50]}...")

                conn.commit()
                print(f"✅ Berhasil menyimpan {saved_count} data ke tbl_berita dan hasil_cleaning.")
                export_to_excel(cleaned_rows)
        else:
            print(f"❌ Gagal terhubung ke detik.com (Status: {response.status_code})")

    except mysql.connector.Error as err:
        print(f"❌ Error Database: {err}")
    except Exception as e:
        print(f"❌ Error Terjadi: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Koneksi database ditutup.")


ambil_judul_detik()

 