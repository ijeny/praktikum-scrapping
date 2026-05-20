import os 
def buat_folder(P1): 
    if not os.path.exists(P1): 
        os.mkdir(P1) 
        print(f"Folder '{P1}' berhasil dibuat.") 
    else: 
        print(f"Folder '{P1}' sudah ada.") 
 
def simpan_data(nama_file, isi_teks): 
    with open(nama_file, 'a') as f: 
        f.write(isi_teks + "\n") 
    print(f"Data berhasil disimpan ke {nama_file} : {os.path.exists(nama_file)}") 


for i in range(1, 6):
    print(f"Proses folder : {os.path.exists(f'Data_Scraping_{i}')}")
    nama_folder = f"Data_Scraping_{i}"
    buat_folder(nama_folder)

    for j in range(1, 6):
        print(f"Proses file : {os.path.exists(f'{nama_folder}/hasil_{j}.txt')}")
        nama_file = f"{nama_folder}/hasil_{j}.txt"
        isi_teks = f"contoh hasil scrapping folder {i} file {j}"
        simpan_data(nama_file, isi_teks)
