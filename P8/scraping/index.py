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

    # Hapus tag HTML (seperti <p>, <br>, dll) menggunakan regex
    teks = re.sub(r'<[^>]*>', '', teks)

    # Hapus backslash (\)
    teks = teks.replace('\\', '')

    # Hapus Emoji dan simbol non-ASCII (seperti 👏, 🔥, dll)
    # Karakter di luar rentang \x00-\x7F akan digantikan dengan spasi
    teks = re.sub(r'[^\x00-\x7F]+', ' ', teks)

    # Hapus karakter whitespace berlebih dan newline
    teks = teks.strip()
    teks = " ".join(teks.split())

    return teks


def normalisasi_url(url):
    if url is None:
        return url
    return url.strip()


def export_to_excel(rows, filename="hasil_cleaning.xlsx"):
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
                waktu_scraping DATETIME,
                isi_berita TEXT
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

                for berita in daftar_berita[:100] :
                    img_tag = berita.find('img')
                    img_url = img_tag.get('src') if img_tag else None
                    judul_asli = " ".join(berita.text.split())

                    # Tahap Cek Duplikasi: Cari judul di tabel tbl_berita
                    cursor.execute("SELECT id FROM tbl_berita WHERE judul = %s", (judul_asli,))
                    if cursor.fetchone():
                        print(f"⏩ Dilewati (Sudah ada): {judul_asli[:50]}...")
                        continue

                    judul_clean = bersihkan_teks(judul_asli)
                    url_link = berita.get('href')
                    url_link_clean = normalisasi_url(url_link)

                    # Scraping Isi Berita (Deep Scraping)
                    try:
                        res_detail = requests.get(url_link, headers=headers, timeout=10)
                        soup_detail = BeautifulSoup(res_detail.text, 'html.parser')

                        # Hapus elemen script dan style agar kontennya tidak dianggap sebagai teks berita
                        for element in soup_detail(['script', 'style']):
                            element.decompose()

                        # DetikInet biasanya menggunakan class detail__body-text untuk isi berita
                        body = soup_detail.select_one('.detail__body-text')
                        raw_isi = body.get_text(separator=' ', strip=True) if body else ""
                    except Exception:
                        raw_isi = "Gagal mengambil konten"

                    isi_berita = bersihkan_teks(raw_isi)

                    # Simpan data mentah ke tabel tbl_berita
                    sql_raw = "INSERT INTO tbl_berita (judul, url_link, url_gambar, isi_berita, waktu_scraping) VALUES (%s, %s, %s, %s, %s)"
                    val_raw = (judul_asli, url_link, img_url, isi_berita, waktu_sekarang)
                    cursor.execute(sql_raw, val_raw)

                    # Simpan data hasil cleaning ke tabel hasil_cleaning
                    sql_clean = (
                        "INSERT INTO hasil_cleaning (judul_asli, judul_clean, url_link, url_link_clean, url_gambar, waktu_scraping, isi_berita) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    )
                    val_clean = (judul_asli, judul_clean, url_link, url_link_clean, img_url, waktu_sekarang, isi_berita)
                    cursor.execute(sql_clean, val_clean)

                    cleaned_rows.append({
                        'judul_asli': judul_asli,
                        'judul_clean': judul_clean,
                        'url_link': url_link,
                        'url_link_clean': url_link_clean,
                        'url_gambar': img_url,
                        'waktu_scraping': waktu_sekarang,
                        'isi_berita': isi_berita    
                    })

                    saved_count += 1
                    print(f"Disimpan: {judul_clean[:50]}...")

                conn.commit()
                print(f"✅ Berhasil menyimpan {saved_count} data ke tbl_berita dan hasil_cleaning.")
                export_to_excel(cleaned_rows)
                return saved_count
        else:
            print(f"❌ Gagal terhubung ke detik.com (Status: {response.status_code})")
            return 0

    except mysql.connector.Error as err:
        print(f"❌ Error Database: {err}")
        return 0
    except Exception as e:
        print(f"❌ Error Terjadi: {e}")
        return 0
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Koneksi database ditutup.")


def jalankan_scraper_otomatis():
    # Menentukan lokasi file log di direktori skrip yang sama
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_log = os.path.join(base_dir, "log_otomasi.txt")

    try:
        inserted = ambil_judul_detik()
        with open(path_log, "a") as log:
            log.write(f"[{datetime.now()}] OTOMASI SUKSES: Berhasil mengarsipkan {inserted} berita baru.\n")
    except Exception as e:
        with open(path_log, "a") as log:
            log.write(f"[{datetime.now()}] OTOMASI GAGAL: Error -> {str(e)}\n")


if __name__ == "__main__":
    jalankan_scraper_otomatis()

 