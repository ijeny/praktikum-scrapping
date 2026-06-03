import os
from datetime import datetime

import mysql.connector
import requests
from bs4 import BeautifulSoup


URL = "https://inet.detik.com/"

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3307")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "ijeny46"),
    "database": os.getenv("MYSQL_DATABASE", "db_scraping"),
}

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
                waktu_scraping DATETIME
            )
            """
        )

        print("Database dan tabel siap digunakan.")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def ambil_judul_detik():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    conn = None
    cursor = None

    try:
        buat_database_dan_tabel()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Terhubung ke database.")

        response = requests.get(URL, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Gagal terhubung ke detik.com (Status: {response.status_code})")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        daftar_berita = soup.select('a[class*="ph_newsfeed_d"]')

        if not daftar_berita:
            print("Tidak ditemukan judul berita di halaman.")
            return

        waktu_sekarang = datetime.now()
        total_disimpan = 0

        for berita in daftar_berita[:25]:
            img_tag = berita.find("img")
            img_url = None

            if img_tag:
                img_url = img_tag.get("src") or img_tag.get("data-src")

            judul = " ".join(berita.get_text().split())
            link = berita.get("href")

            if not judul or not link:
                continue

            sql = (
                "INSERT INTO tbl_berita "
                "(judul, url_link, url_gambar, waktu_scraping) "
                "VALUES (%s, %s, %s, %s)"
            )
            val = (judul, link, img_url, waktu_sekarang)

            cursor.execute(sql, val)
            total_disimpan += 1
            print(f"Disimpan: {judul[:50]}...")

        conn.commit()
        print(f"Berhasil menyimpan {total_disimpan} data ke database.")

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


ambil_judul_detik()
