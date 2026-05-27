import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def buat_folder(P1):
    folder_sudah_ada = os.path.exists(P1)
    print(f"Apakah folder ({P1}) sudah ada? : {folder_sudah_ada}")

    if not folder_sudah_ada:
        os.mkdir(P1)
        print(f"Folder '{P1}' berhasil dibuat.")
    else:
        print(f"Folder '{P1}' sudah ada.")


def simpan_data(nama_file, isi_teks):
    file_sudah_ada = os.path.exists(nama_file)
    print(f"Apakah file ({nama_file}) sudah ada? : {file_sudah_ada}")

    with open(nama_file, 'a') as f:
        f.write(isi_teks + "\n")
    print(f"Data berhasil disimpan ke {nama_file}")


for i in range(1, 6):
    nama_folder = os.path.join(BASE_DIR, f"Data_Scraping_{i}")
    buat_folder(nama_folder)

    for j in range(1, 6):
        nama_file = os.path.join(nama_folder, f"hasil_{j}.txt")
        isi_teks = f"contoh hasil scrapping folder {i} file {j}"
        simpan_data(nama_file, isi_teks)