import { db } from "@/app/lib/db";
import { NextRequest } from "next/server";
import { NextResponse } from "next/server";

interface Berita {
  id: number;
  judul: string;
  judul_asli: string;
  judul_clean: string;
  url_link: string;
  url_gambar: string | null;
  isi_berita: string | null;
  kategori: string | null;
  waktu_scraping: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const page = Math.max(Number(searchParams.get("page")) || 1, 1);
    const limit = Math.min(Math.max(Number(searchParams.get("limit")) || 9, 1), 30);
    const offset = (page - 1) * limit;

    const [countRows] = await db.query("SELECT COUNT(*) AS total FROM tbl_berita");
    const total = Number((countRows as { total: number }[])[0]?.total || 0);

    // Mengambil data per halaman agar tidak memuat seluruh tabel ke memori.
    const [rows] = await db.query(
      `SELECT
        id,
        judul,
        judul AS judul_asli,
        judul AS judul_clean,
        url_link,
        url_gambar,
        isi_berita,
        kategori,
        waktu_scraping
      FROM tbl_berita
      ORDER BY waktu_scraping DESC
      LIMIT ? OFFSET ?`,
      [limit, offset],
    );

    const dataBerita = rows as Berita[];

    return NextResponse.json(
      {
        success: true,
        message: "Berhasil mengambil data berita",
        total,
        page,
        limit,
        data: dataBerita,
      },
      { status: 200 },
    );
  } catch (error) {
    console.error("Database Error:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Terjadi kesalahan pada server";

    return NextResponse.json(
      {
        success: false,
        message: "Gagal memuat data dari database",
        error: errorMessage,
      },
      { status: 500 },
    );
  }
}
