import os
from datetime import datetime
from urllib.parse import urljoin

import mysql.connector
import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL = "https://inet.detik.com/indeks"

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "ijeny46",
    "database": "db_scraping",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )
}

KANAL_TEKNOLOGI = {
    "consumer",
    "cyberlife",
    "games-news",
    "science",
    "telecommunication",
}


def buat_folder(nama_folder):
    if not os.path.exists(nama_folder):
        os.mkdir(nama_folder)
        print(f"Folder '{nama_folder}' berhasil dibuat.")
    else:
        print(f"Folder '{nama_folder}' sudah ada.")


def tulis_log(judul, link):
    nama_folder = os.path.join(BASE_DIR, "Scraping_Data")

    if not os.path.exists(nama_folder):
        buat_folder(nama_folder)

    nama_file = os.path.join(nama_folder, "log_db.txt")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(nama_file, "a", encoding="utf-8") as file:
        file.write(f"{waktu} | Berhasil simpan data: {judul} | {link}\n")


def tentukan_kategori(link):
    bagian_url = link.split("inet.detik.com/", 1)
    if len(bagian_url) < 2:
        return "Umum"

    kanal = bagian_url[1].split("/", 1)[0]
    return "Teknologi" if kanal in KANAL_TEKNOLOGI else "Umum"


def buat_database_dan_tabel():
    conn = None
    cursor = None
    database = DB_CONFIG["database"].replace("`", "``")

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        cursor.execute(f"USE `{database}`")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tbl_berita (
                id INT AUTO_INCREMENT PRIMARY KEY,
                judul VARCHAR(255),
                url_link TEXT,
                url_gambar TEXT,
                isi_berita LONGTEXT,
                kategori VARCHAR(50) DEFAULT 'Teknologi',
                waktu_scraping DATETIME
            )
            """
        )

        cursor.execute("SHOW COLUMNS FROM tbl_berita")
        kolom_tabel = {row[0] for row in cursor.fetchall()}

        if "isi_berita" not in kolom_tabel:
            cursor.execute("ALTER TABLE tbl_berita ADD COLUMN isi_berita LONGTEXT")

        if "kategori" not in kolom_tabel:
            cursor.execute(
                "ALTER TABLE tbl_berita ADD COLUMN kategori VARCHAR(50) DEFAULT 'Teknologi'"
            )
            cursor.execute(
                "UPDATE tbl_berita SET kategori = 'Teknologi' WHERE kategori IS NULL"
            )

        if "waktu_scraping" not in kolom_tabel:
            cursor.execute("ALTER TABLE tbl_berita ADD COLUMN waktu_scraping DATETIME")

        if "tanggal_scraping" in kolom_tabel:
            cursor.execute(
                """
                UPDATE tbl_berita
                SET waktu_scraping = tanggal_scraping
                WHERE waktu_scraping IS NULL
                """
            )
            cursor.execute("ALTER TABLE tbl_berita DROP COLUMN tanggal_scraping")

        conn.commit()
        print("Database dan tabel siap digunakan.")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def ambil_detail_berita(link):
    response = requests.get(link, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.select_one(".detail__body-text") or soup.select_one(".detail__body")
    isi_berita = ""

    if body:
        for tag in body.select("script, style, iframe, .ads, .parallaxindetail"):
            tag.decompose()

        paragraf = [
            " ".join(p.get_text(" ", strip=True).split())
            for p in body.find_all("p")
        ]
        isi_berita = "\n".join(p for p in paragraf if p)

    meta_gambar = soup.select_one('meta[property="og:image"]')
    url_gambar = meta_gambar.get("content") if meta_gambar else None

    return isi_berita, url_gambar


def ambil_berita_detik():
    hasil = []
    link_ditemukan = set()

    for halaman in range(1, 6):
        url_indeks = URL if halaman == 1 else f"{URL}?page={halaman}"
        response = requests.get(url_indeks, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        daftar_berita = soup.select('a[class*="ph_newsfeed_d"]')

        if not daftar_berita:
            break

        for berita in daftar_berita:
            judul = " ".join(berita.get_text(" ", strip=True).split())
            link = berita.get("href")

            if not judul or not link:
                continue

            link = urljoin(url_indeks, link)

            if link in link_ditemukan:
                continue

            img_tag = berita.find("img")
            url_gambar = None

            if img_tag:
                url_gambar = img_tag.get("src") or img_tag.get("data-src")

            isi_berita, gambar_detail = ambil_detail_berita(link)

            if not isi_berita:
                print(f"Isi berita kosong, dilewati: {judul[:50]}...")
                continue

            if not url_gambar:
                url_gambar = gambar_detail

            hasil.append(
                {
                    "judul": judul,
                    "url_link": link,
                    "url_gambar": url_gambar,
                    "isi_berita": isi_berita,
                    "kategori": tentukan_kategori(link),
                    "waktu_scraping": datetime.now(),
                }
            )
            link_ditemukan.add(link)

            if len(hasil) == 20:
                return hasil

    return hasil


def simpan_berita_ke_database(daftar_berita):
    conn = None
    cursor = None

    try:
        buat_database_dan_tabel()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Terhubung ke database.")

        total_disimpan = 0
        total_duplikat = 0

        for berita in daftar_berita:
            cursor.execute(
                "SELECT COUNT(*) FROM tbl_berita WHERE judul = %s",
                (berita["judul"],),
            )
            sudah_ada = cursor.fetchone()[0] > 0

            if sudah_ada:
                total_duplikat += 1
                print(f"Duplikat, tidak disimpan: {berita['judul'][:50]}...")
                continue

            sql = (
                "INSERT INTO tbl_berita "
                "(judul, url_link, url_gambar, isi_berita, kategori, waktu_scraping) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            val = (
                berita["judul"],
                berita["url_link"],
                berita["url_gambar"],
                berita["isi_berita"],
                berita["kategori"],
                berita["waktu_scraping"],
            )

            cursor.execute(sql, val)
            total_disimpan += 1
            tulis_log(berita["judul"], berita["url_link"])
            print(f"Disimpan: {berita['judul'][:50]}...")

        conn.commit()
        print(f"Berhasil menyimpan {total_disimpan} data ke database.")
        print(f"Data duplikat dilewati: {total_duplikat}.")
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"Error Database: {err}")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error Terjadi: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Koneksi database ditutup.")


def main():
    daftar_berita = ambil_berita_detik()

    if not daftar_berita:
        print("Tidak ditemukan berita dari Detik Inet.")
        return

    simpan_berita_ke_database(daftar_berita)


if __name__ == "__main__":
    main()
