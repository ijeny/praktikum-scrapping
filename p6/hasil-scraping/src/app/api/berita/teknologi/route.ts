import { db } from "@/lib/db";
import { NextResponse } from "next/server";

interface Berita {
  id: number;
  judul: string;
  url_link: string;
  url_gambar: string | null;
  isi_berita: string | null;
  kategori: string;
  waktu_scraping: string;
}

export async function GET() {
  try {
    const [rows] = await db.query(
      `SELECT *
       FROM tbl_berita
       WHERE kategori = 'Teknologi'
       ORDER BY waktu_scraping DESC
       LIMIT 5`,
    );

    const dataBerita = rows as Berita[];

    return NextResponse.json(
      {
        success: true,
        message: "Berhasil mengambil berita kategori Teknologi",
        total: dataBerita.length,
        data: dataBerita,
      },
      { status: 200 },
    );
  } catch (error) {
    console.error("Database Error:", error);

    return NextResponse.json(
      {
        success: false,
        message: "Gagal mengambil data",
      },
      { status: 500 },
    );
  }
}
