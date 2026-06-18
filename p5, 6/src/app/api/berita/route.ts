import { db } from '@/lib/db';
import { NextResponse } from 'next/server';

/**
 * Interface untuk mencocokkan struktur kolom di tabel tbl_berita
 */
interface Berita {
  id: number;
  judul: string;
  url_link: string;
  url_gambar: string | null;
  isi_berita: string | null;
  waktu_scraping: string;
}

export async function GET() {
  try {
    // Mengambil semua data dari tbl_berita diurutkan dari yang terbaru
    const [rows] = await db.query('SELECT * FROM hasil_cleaning ORDER BY waktu_scraping DESC');

    const dataBerita = rows as Berita[];

    return NextResponse.json({
      success: true,
      message: "Berhasil mengambil data berita",
      total: dataBerita.length,
      data: dataBerita
    }, { status: 200 });

  } catch (error) {
    console.error("Database Error:", error);
    const errorMessage = error instanceof Error ? error.message : "Terjadi kesalahan pada server";
    
    return NextResponse.json({
      success: false,
      message: "Gagal memuat data dari database",
      error: errorMessage
    }, { status: 500 });
  }
}
