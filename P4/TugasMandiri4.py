import os
import re
import unicodedata
from datetime import datetime

import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "hasil_cleaning.xlsx")

NAMA_BULAN = {
    "januari": "01",
    "februari": "02",
    "maret": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "agustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "desember": "12",
}

SINGKATAN = {"ai", "ri", "nik", "lg", "amd", "ace", "hp"}


def bersihkan_judul(judul):
    teks = unicodedata.normalize("NFKC", judul)
    teks = re.sub(r"\s+", " ", teks).strip()
    kata_normal = []

    for kata in teks.split(" "):
        pembuka = re.match(r"^[^A-Za-z0-9%]+", kata)
        penutup = re.search(r"[^A-Za-z0-9%]+$", kata)
        prefix = pembuka.group(0) if pembuka else ""
        suffix = penutup.group(0) if penutup else ""
        inti = kata[len(prefix): len(kata) - len(suffix) if suffix else len(kata)]

        if inti.lower() in SINGKATAN:
            kata_normal.append(f"{prefix}{inti.upper()}{suffix}")
        else:
            kata_normal.append(kata.capitalize())

    return " ".join(kata_normal)


def format_waktu_public(waktu_public):
    tanggal = re.sub(r"\s+", " ", waktu_public).strip().lower()
    bagian = tanggal.split(" ")

    if len(bagian) != 3:
        raise ValueError(f"Format tanggal tidak valid: {waktu_public}")

    hari, bulan, tahun = bagian
    bulan_angka = NAMA_BULAN.get(bulan)

    if bulan_angka is None:
        raise ValueError(f"Nama bulan tidak valid: {waktu_public}")

    tanggal_datetime = datetime(int(tahun), int(bulan_angka), int(hari))
    return tanggal_datetime.strftime("%Y%m%d")


def buat_raw_data():
    return [
        {
            "Judul": "  AI Ada di Mana-mana, Traffic Internet Diramal Naik 5 Kali Lipat  ",
            "Waktu_Public": "18 Mei 2026",
        },
        {
            "Judul": "Menkomdigi:   Transformasi Digital RI Harus Dibangun Secara Komunal",
            "Waktu_Public": "19 Mei 2026",
        },
        {
            "Judul": "\t19% Penduduk RI Belum Terhubung Internet, Ini Janji Pemerintah",
            "Waktu_Public": "20 Mei 2026",
        },
        {
            "Judul": "Beli Nomor HP Baru Tak Cukup NIK, Pekan Depan Wajib Verifikasi Wajah",
            "Waktu_Public": "21 Mei 2026",
        },
        {
            "Judul": " Satelit Jadi Kunci Pemerataan Akses Digital hingga Pelosok RI ",
            "Waktu_Public": "22 Mei 2026",
        },
        {
            "Judul": "Schneider OffGrid Rilis di RI, Power Station untuk Kemah & Listrik Padam",
            "Waktu_Public": "23 Mei 2026",
        },
        {
            "Judul": "AMD dan Intel Garap ACE Buat Tantang Dominasi Nvidia di AI",
            "Waktu_Public": "24 Mei 2026",
        },
        {
            "Judul": "Smartphone Bagus    Bukan Cuma Soal Harga",
            "Waktu_Public": "25 Mei 2026",
        },
        {
            "Judul": "\nTelkomsel Ubah Ribuan Langkah di Digiland Run 2026 Jadi Pohon Mangrove\n",
            "Waktu_Public": "26 Mei 2026",
        },
        {
            "Judul": "Shin Ye Eun Meriahkan Housewarming by LG di Indonesia",
            "Waktu_Public": "27 Mei 2026",
        },
    ]


def cleaning_data(raw_data):
    hasil_cleaning = []

    for item in raw_data:
        hasil_cleaning.append(
            {
                "Judul_Raw": item["Judul"],
                "Waktu_Public_Raw": item["Waktu_Public"],
                "Judul_Clean": bersihkan_judul(item["Judul"]),
                "Waktu_Public_Clean": format_waktu_public(item["Waktu_Public"]),
            }
        )

    return hasil_cleaning


def export_excel(df, filename):
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Hasil Cleaning", index=False)
        worksheet = writer.sheets["Hasil Cleaning"]

        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                nilai = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(nilai))

            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)


def main():
    raw_data = buat_raw_data()
    hasil_cleaning = cleaning_data(raw_data)
    df = pd.DataFrame(hasil_cleaning)

    export_excel(df, OUTPUT_FILE)

    print("Hasil Cleansed Data:")
    print(df[["Judul_Clean", "Waktu_Public_Clean"]].to_string(index=False))
    print(f"\nData berhasil diekspor ke: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
