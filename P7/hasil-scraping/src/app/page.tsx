"use client"; // Wajib ditulis di baris pertama untuk menandakan Client Component

import { useEffect, useState } from "react";
import { Inter } from "next/font/google";
const inter = Inter({ subsets: ["latin"], weight: ["400", "600"] });

interface Berita {
  id: number;
  judul: string;
  judul_asli: string;
  judul_clean: string;
  url_link: string;
  url_gambar: string | null;
  isi_berita: string | null;
  kategori?: string | null;
  waktu_scraping: string;
}

// Helper to safely parse and format date strings or timestamps
function formatDate(value: string | number | Date | null | undefined): string {
  if (!value) {
    return "Tanggal tidak valid";
  }

  let date = new Date(value);
  if (isNaN(date.getTime())) {
    // Try treating as Unix timestamp (seconds)
    const numeric = Number(value);
    if (!isNaN(numeric)) {
      date = new Date(numeric * 1000);
    }
  }
  if (isNaN(date.getTime())) {
    return "Tanggal tidak valid";
  }
  return date.toLocaleDateString("id-ID");
}

export default function BeritaPage() {
  const [daftarBerita, setDaftarBerita] = useState<Berita[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBerita, setSelectedBerita] = useState<Berita | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9; // 3 columns x 3 rows per page

  // Mengambil data dari API secara otomatis saat halaman dibuka
  useEffect(() => {
    fetch("/api/berita")
      .then((res) => res.json())
      .then((json) => {
        if (json.success) {
          setDaftarBerita(json.data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Gagal mengambil data API:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50">
        <p className="text-xl font-semibold text-blue-600 animate-pulse">
          Memuat Data Berita STIKOM...
        </p>
      </div>
    );
  }

  return (
    <div
      className={`${inter.className} min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-50 flex flex-col`}
    >
      {/* HEADER */}
      <header className="bg-indigo-800 text-white shadow-lg p-4 flex items-center justify-between">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold tracking-wider">
            PORTAL DATA SCRAPING STIKOM
          </h1>
          <span className="bg-blue-800 text-xs px-3 py-1.5 rounded-full font-mono">
            XAMPP & MySQL Active
          </span>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-grow container mx-auto p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 border-b-2 border-blue-500 pb-2 inline-block">
          Hasil Scraping Detik Inet Terbaru
        </h2>

        <div className="bg-white/90 rounded-xl shadow-md p-5 mb-6 border-l-4 border-indigo-600">
          <p className="text-sm font-semibold text-gray-500 uppercase">
            Dashboard Statistik
          </p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            Total Berita Dimuat: {daftarBerita.length}
          </p>
        </div>

        {daftarBerita.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <p className="text-gray-600 text-lg">
              Belum ada data di database. Pastikan engine Python Anda sudah
              dijalankan.
            </p>
          </div>
        ) : (
          /* GRID SYSTEM: 1 Kolom di HP, 2 Kolom di Tablet, 3 Kolom di Laptop/PC */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {daftarBerita
              .slice(
                (currentPage - 1) * itemsPerPage,
                currentPage * itemsPerPage,
              )
              .map((berita) => {
                const kategoriBerita = berita.kategori || "Umum";
                const kategoriBadgeClass =
                  kategoriBerita === "Teknologi"
                    ? "bg-green-100 text-green-800"
                    : "bg-blue-100 text-blue-800";

                return (
                  <div
                    key={berita.id}
                    className="cursor-pointer"
                    onClick={() => setSelectedBerita(berita)}
                  >
                  <div className="bg-white/90 rounded-xl shadow-lg overflow-hidden hover:shadow-2xl hover:scale-105 transition-all duration-300 flex flex-col backdrop-blur-sm">
                    {/* Bagian Gambar Berita */}
                    <div className="h-48 w-full bg-gray-200 relative">
                      {berita.url_gambar ? (
                        <img
                          src={
                            berita.url_gambar.startsWith("http")
                              ? berita.url_gambar
                              : `${process.env.NEXT_PUBLIC_BASE_URL}/${berita.url_gambar}`
                          }
                          alt={berita.judul_clean}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          No Image Available
                        </div>
                      )}
                    </div>

                    {/* Konten Teks Kartu */}
                    <div className="p-5 flex-grow flex flex-col justify-between">
                      <div>
                        <span
                          className={`inline-block ${kategoriBadgeClass} text-xs font-bold px-2.5 py-1 rounded uppercase mb-3`}
                        >
                          {kategoriBerita}
                        </span>
                        <h3 className="font-bold text-gray-900 text-md leading-snug line-clamp-2 hover:text-indigo-600 transition-colors duration-200">
                          {berita.judul_clean}
                        </h3>
                      </div>

                      <div className="mt-5 pt-3 border-t border-gray-100 flex items-center justify-between">
                        <span className="text-xs text-gray-400 font-mono">
                          {formatDate(berita.waktu_scraping)}
                        </span>
                        <span className="text-sm text-indigo-600 font-bold hover:text-indigo-800 inline-flex items-center transition-colors duration-200">
                          Buka Sumber →
                        </span>
                      </div>
                    </div>
                  </div>
                  </div>
                );
              })}
          </div>
        )}
      </main>

      {/* PAGINATION */}
      {daftarBerita.length > itemsPerPage && (
        <div className="flex justify-center items-center space-x-4 mt-6">
          <button
            className="px-5 py-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-200"
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            ← Prev
          </button>
          <span className="text-gray-800 font-medium">
            Page {currentPage} of{" "}
            {Math.ceil(daftarBerita.length / itemsPerPage)}
          </span>
          <button
            className="px-5 py-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-200"
            onClick={() =>
              setCurrentPage((prev) =>
                Math.min(
                  prev + 1,
                  Math.ceil(daftarBerita.length / itemsPerPage),
                ),
              )
            }
            disabled={
              currentPage === Math.ceil(daftarBerita.length / itemsPerPage)
            }
          >
            Next →
          </button>
        </div>
      )}
      {/* FOOTER */}
      {selectedBerita && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 relative max-h-[90vh] overflow-y-auto shadow-2xl">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 bg-gray-100 p-1 rounded-full"
              onClick={() => setSelectedBerita(null)}
            >
              ✖
            </button>
            <div className="h-64 w-full bg-gray-200 mb-4 flex-shrink-0 rounded-lg overflow-hidden">
              <img
                src={
                  selectedBerita.url_gambar?.startsWith("http")
                    ? selectedBerita.url_gambar
                    : `${process.env.NEXT_PUBLIC_BASE_URL}/${selectedBerita.url_gambar}`
                }
                alt={selectedBerita.judul_asli}
                className="w-full h-full object-cover"
              />
            </div>
            <h2 className="font-bold text-xl mb-2 text-gray-900">
              {selectedBerita.judul_asli}
            </h2>
            <p className="text-sm text-gray-500 mb-2">
              {selectedBerita.kategori || "Umum"}
            </p>
            <p className="text-xs text-gray-400 mb-4">
              {formatDate(selectedBerita.waktu_scraping)}
            </p>
            {selectedBerita.isi_berita && (
              <p className="text-gray-700 mb-4 leading-relaxed">
                {selectedBerita.isi_berita}
              </p>
            )}
            <a
              href={selectedBerita.url_link}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block text-indigo-600 font-medium hover:text-indigo-800 transition-colors duration-200"
            >
              Buka Sumber →
            </a>
          </div>
        </div>
      )}
      <footer className="bg-gray-800 text-gray-400 text-center p-4 text-xs">
        <p>
          &copy; {new Date().getFullYear()} Praktikum Data Scraping - S1 Sistem
          Informasi STIKOM PGRI Banyuwangi
        </p>
        <p className="mt-2">
          1124102181{" "}
          <a
            href="https://github.com/ijeny"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-300 hover:text-blue-200 underline"
          >
            Imtinan Jeny Maulidah Belvariyanto
          </a>{" "}
          | 1124102166{" "}
          <a
            href="https://github.com/hivicode"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-300 hover:text-blue-200 underline"
          >
            Bintang Fathir Fadilah Achmad
          </a>
        </p>
      </footer>
    </div>
  );
}
