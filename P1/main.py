import os 
# Fungsi untuk mengecek dan membuat folder 
def buat_folder(P1): 
    if not os.path.exists(P1): 
        os.mkdir(P1) 
        print(f"Folder '{P1}' berhasil dibuat.") 
    else: 
        print(f"Folder '{P1}' sudah ada.") 
 
# Memanggil fungsi 
buat_folder("Data_Scraping") 
 
def simpan_data(nama_file, isi_teks): 
    # 'a' berarti append (menambah tanpa menghapus isi lama) 
    with open(nama_file, 'a') as f: 
        f.write(isi_teks + "\n") 
    print(f"Data berhasil disimpan ke {nama_file}") 
 
# Menjalankan fungsi simpan 
path_file = "Data_Scraping/hasil.txt" 
simpan_data(path_file, "Contoh hasil scraping dari quotes.toscrape.com") 
