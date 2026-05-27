import requests  
from bs4 import BeautifulSoup  

def ambil_judul_detik():  
    url = "https://inet.det"  

    # Mengambil HTML dari detik  
    response = requests.get(url)  
    if response.status_code == 200:  

        # Parsing HTML  
        soup = BeautifulSoup(response.text, 'html.parser')  

        # Mencari semua elemen judul berita  
        daftar_berita = soup.select('a[class*="ph_newsfeed_d"]')  
        if not daftar_berita:  
            hasil = ['Tidak ditemukan judul berita di halaman. Struktur HTML mungkin berubah.']  
        else:  
            hasil = []  
            for berita in daftar_berita[:5]:   
                hasil.append(f"Judul: {berita.text.strip()}")  
                hasil.append(f"Link : {berita['href']}")  
                hasil.append('')  
         
        with open('hasil.txt', 'w', encoding='utf-8') as file:  
            file.write('\n'.join(hasil))  
        for baris in hasil:  
            print(baris)  
    else:  
        print("Gagal terhubung ke detik.com")  

ambil_judul_detik() 