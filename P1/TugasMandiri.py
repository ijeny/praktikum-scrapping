import os 
def buat_folder(P1): 
    folder_sudah_ada = os.path.exists(P1)
    print(f"Validasi sebelum folder dibuat ({P1}) : {folder_sudah_ada}")

    if not folder_sudah_ada: 
        os.mkdir(P1) 
        print(f"Folder '{P1}' berhasil dibuat.") 
    else: 
        print(f"Folder '{P1}' sudah ada.") 
 
def simpan_data(nama_file, isi_teks): 
    file_sudah_ada = os.path.exists(nama_file)
    print(f"Validasi sebelum file dibuat ({nama_file}) : {file_sudah_ada}")

    with open(nama_file, 'a') as f: 
        f.write(isi_teks + "\n") 
    print(f"Data berhasil disimpan ke {nama_file}") 


for i in range(1, 6):
    nama_folder = f"Data_Scraping_{i}"
    buat_folder(nama_folder)

    for j in range(1, 6):
        nama_file = f"{nama_folder}/hasil_{j}.txt"
        isi_teks = f"contoh hasil scrapping folder {i} file {j}"
        simpan_data(nama_file, isi_teks)
