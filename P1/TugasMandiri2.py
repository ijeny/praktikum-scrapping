import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def buat_folder(nama_folder):
    if not os.path.exists(nama_folder):
        os.mkdir(nama_folder)
        print(f"Folder '{nama_folder}' berhasil dibuat.")
    else:
        print(f"Folder '{nama_folder}' sudah ada.")


def scraping_kompas_to_file():
    url = "https://www.kompas.com/tag/inet"
    nama_folder = os.path.join(BASE_DIR, "Scraping_Data")

    if not os.path.exists(nama_folder):
        buat_folder(nama_folder)

    tanggal = datetime.now().strftime("%Y_%m_%d")
    nama_file = os.path.join(nama_folder, f"hasil_{tanggal}.txt")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        print("Gagal mengambil data dari Kompas.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    daftar_berita = soup.select("div.articleItem a.article-link")[:10]

    hasil = []
    for nomor, berita in enumerate(daftar_berita, start=1):
        judul = berita.select_one("h2.articleTitle")
        link = berita.get("href")

        if judul and link:
            hasil.append(f"{nomor}. Judul: {judul.get_text(strip=True)}")
            hasil.append(f"   Link : {link}")
            hasil.append("")

    with open(nama_file, "w", encoding="utf-8") as file:
        file.write("\n".join(hasil))

    print(f"Berhasil menyimpan {len(hasil) // 3} berita ke {nama_file}")


scraping_kompas_to_file()
