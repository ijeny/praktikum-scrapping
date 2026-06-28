"use client";

import {
  ChevronLeft,
  ChevronRight,
  Clock,
  Database,
  ExternalLink,
  Layers,
  Moon,
  Newspaper,
  Sun,
  X,
} from "lucide-react";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });
const MIN_LOADING_DURATION = 2500;

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

const NIGHT = {
  bg: "#0b0f1e",
  card: "#151e35",
  border: "rgba(66,116,217,0.15)",
  borderHover: "rgba(149,204,221,0.4)",
  fg: "#d0e7e6",
  fgSub: "#95ccdd",
  muted: "#7893bd",
  blue: "#4274d9",
  headerBg: "rgba(11,15,30,0.88)",
  shadow: "rgba(0,0,0,0.55)",
  divider: "rgba(66,116,217,0.12)",
  statBg: "#131c30",
};

const DAY = {
  bg: "#eef6f6",
  card: "#ffffff",
  border: "rgba(41,54,129,0.12)",
  borderHover: "rgba(66,116,217,0.45)",
  fg: "#1a2540",
  fgSub: "#293681",
  muted: "#6b84b2",
  blue: "#4274d9",
  headerBg: "rgba(238,246,246,0.92)",
  shadow: "rgba(41,54,129,0.12)",
  divider: "rgba(41,54,129,0.08)",
  statBg: "#f0f9f9",
};

type Theme = typeof NIGHT;

function formatDate(value: string | number | Date | null | undefined): string {
  if (!value) return "-";

  const date = new Date(value);
  if (isNaN(date.getTime())) return "-";

  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(value: string | number | Date | null | undefined): string {
  if (!value) return "Belum ada data";

  const date = new Date(value);
  if (isNaN(date.getTime())) return "-";

  return date.toLocaleString("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getImageUrl(url: string | null): string | null {
  if (!url) return null;
  return url.startsWith("http") ? url : `/${url.replace(/^\/+/, "")}`;
}

function getBadgeStyle(
  kategori: string,
  dark: boolean,
): { bg: string; color: string; border: string } {
  const map: Record<string, { dark: [string, string, string]; light: [string, string, string] }> = {
    Teknologi: {
      dark: ["rgba(34,197,94,0.12)", "#4ade80", "rgba(34,197,94,0.3)"],
      light: ["rgba(22,163,74,0.1)", "#16a34a", "rgba(22,163,74,0.3)"],
    },
    Sains: {
      dark: ["rgba(251,146,60,0.12)", "#fb923c", "rgba(251,146,60,0.3)"],
      light: ["rgba(234,88,12,0.1)", "#ea580c", "rgba(234,88,12,0.25)"],
    },
    Gadget: {
      dark: ["rgba(167,139,250,0.13)", "#c084fc", "rgba(167,139,250,0.3)"],
      light: ["rgba(124,58,237,0.1)", "#7c3aed", "rgba(124,58,237,0.25)"],
    },
    Umum: {
      dark: ["rgba(66,116,217,0.14)", "#7baef5", "rgba(66,116,217,0.35)"],
      light: ["rgba(66,116,217,0.1)", "#4274d9", "rgba(66,116,217,0.3)"],
    },
  };

  const entry = map[kategori] ?? map.Umum;
  const [bg, color, border] = dark ? entry.dark : entry.light;
  return { bg, color, border };
}

export default function BeritaPage() {
  const [daftarBerita, setDaftarBerita] = useState<Berita[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasLoadingImage, setHasLoadingImage] = useState(true);
  const [selectedBerita, setSelectedBerita] = useState<Berita | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [dark, setDark] = useState(false);
  const itemsPerPage = 9;

  const theme: Theme = dark ? NIGHT : DAY;
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
  const pagedBerita = useMemo(() => daftarBerita, [daftarBerita]);

  useEffect(() => {
    const startedAt = Date.now();

    const finishLoading = () => {
      const remainingTime = Math.max(0, MIN_LOADING_DURATION - (Date.now() - startedAt));
      window.setTimeout(() => setLoading(false), remainingTime);
    };

    fetch(`/api/berita?page=${currentPage}&limit=${itemsPerPage}`)
      .then((res) => res.json())
      .then((json) => {
        setDaftarBerita(json.success ? json.data : []);
        setTotalItems(json.success ? json.total || 0 : 0);
        finishLoading();
      })
      .catch((err) => {
        console.error("Gagal mengambil data API:", err);
        setTotalItems(0);
        finishLoading();
      });
  }, [currentPage]);

  if (loading) {
    return (
      <div
        className={`${inter.className} flex min-h-screen flex-col items-center justify-center gap-5 px-6 text-center`}
        style={{ background: DAY.bg, color: DAY.fg }}
      >
        {hasLoadingImage ? (
          <Image
            src="/loading.webp"
            alt="Memuat data scraping"
            width={180}
            height={180}
            className="h-40 w-40 object-contain sm:h-44 sm:w-44"
            priority
            unoptimized
            onError={() => setHasLoadingImage(false)}
          />
        ) : (
          <div
            className="h-10 w-10 animate-spin rounded-full border-2 border-t-transparent"
            style={{ borderColor: DAY.blue, borderTopColor: "transparent" }}
          />
        )}
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: DAY.muted }}>
            Memuat data scraping
          </p>
          <p className="mt-2 text-sm" style={{ color: DAY.fgSub }}>
            Menyiapkan hasil berita terbaru
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`${inter.className} flex min-h-screen flex-col`}
      style={{
        background: theme.bg,
        color: theme.fg,
        transition: "background 0.3s, color 0.3s",
      }}
    >
      <header
        className="sticky top-0 z-40 border-b"
        style={{
          background: theme.headerBg,
          backdropFilter: "blur(16px)",
          borderColor: theme.border,
        }}
      >
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2.5">
            <Newspaper size={17} style={{ color: theme.fgSub, flexShrink: 0 }} />
            <span className="text-sm font-semibold tracking-tight">
              STIKOM<span style={{ color: theme.blue }}>.</span>SCRAPER
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div
              className="hidden items-center gap-1.5 rounded-full px-3 py-1 text-xs sm:flex"
              style={{
                background: dark ? "rgba(34,197,94,0.1)" : "rgba(22,163,74,0.08)",
                border: dark ? "1px solid rgba(34,197,94,0.25)" : "1px solid rgba(22,163,74,0.2)",
                color: dark ? "#4ade80" : "#16a34a",
              }}
            >
              <span
                className="h-1.5 w-1.5 animate-pulse rounded-full"
                style={{ background: dark ? "#4ade80" : "#16a34a" }}
              />
              XAMPP & MySQL Active
            </div>

            <button
              aria-label={dark ? "Aktifkan mode terang" : "Aktifkan mode gelap"}
              className="flex h-9 w-9 items-center justify-center rounded-xl border"
              onClick={() => setDark((value) => !value)}
              style={{
                background: theme.card,
                borderColor: theme.border,
                color: theme.fgSub,
              }}
            >
              {dark ? <Sun size={15} /> : <Moon size={15} />}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-grow px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
        <section className="mb-10">
          <p className="mb-2 text-xs font-semibold uppercase tracking-widest" style={{ color: theme.muted }}>
            Portal Data Scraping
          </p>
          <h1 className="text-3xl font-bold leading-tight sm:text-4xl" style={{ color: theme.fg }}>
            Hasil Scraping <span style={{ color: theme.fgSub }}>Detik Inet</span>
          </h1>
        </section>

        <section
          className="mb-10 flex flex-col gap-4 rounded-2xl border p-5 sm:flex-row sm:items-center sm:justify-between"
          style={{ background: theme.statBg, borderColor: theme.border }}
        >
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl"
              style={{ background: dark ? "rgba(66,116,217,0.15)" : "rgba(66,116,217,0.1)" }}
            >
              <Database size={18} style={{ color: theme.blue }} />
            </div>
            <div>
              <p className="text-xs" style={{ color: theme.muted }}>
                Total Artikel
              </p>
              <p className="text-2xl font-bold" style={{ color: theme.fg }}>
                {totalItems}
              </p>
            </div>
          </div>
          <div className="sm:text-right">
            <p className="mb-0.5 text-xs" style={{ color: theme.muted }}>
              Pembaruan Terakhir
            </p>
            <p className="text-sm font-medium" style={{ color: theme.fgSub }}>
              {formatDateTime(daftarBerita[0]?.waktu_scraping)}
            </p>
          </div>
        </section>

        {daftarBerita.length === 0 ? (
          <section className="flex flex-col items-center justify-center gap-4 py-24 text-center">
            <Layers size={40} style={{ color: theme.borderHover }} />
            <p className="text-sm" style={{ color: theme.muted }}>
              Belum ada data. Jalankan engine Python terlebih dahulu.
            </p>
          </section>
        ) : (
          <>
            <section className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {pagedBerita.map((berita) => {
                const kategori = berita.kategori || "Umum";
                const badge = getBadgeStyle(kategori, dark);
                const imageUrl = getImageUrl(berita.url_gambar);

                return (
                  <article
                    key={berita.id}
                    className="group flex cursor-pointer flex-col overflow-hidden rounded-2xl border"
                    onClick={() => setSelectedBerita(berita)}
                    style={{
                      background: theme.card,
                      borderColor: theme.border,
                      transition: "border-color 0.25s, transform 0.25s, box-shadow 0.25s",
                    }}
                    onMouseEnter={(event) => {
                      event.currentTarget.style.borderColor = theme.borderHover;
                      event.currentTarget.style.transform = "translateY(-3px)";
                      event.currentTarget.style.boxShadow = `0 20px 48px ${theme.shadow}`;
                    }}
                    onMouseLeave={(event) => {
                      event.currentTarget.style.borderColor = theme.border;
                      event.currentTarget.style.transform = "translateY(0)";
                      event.currentTarget.style.boxShadow = "none";
                    }}
                  >
                    <div className="h-44 w-full flex-shrink-0 overflow-hidden" style={{ background: dark ? "#1a2540" : "#daeef0" }}>
                      {imageUrl ? (
                        <img
                          src={imageUrl}
                          alt={berita.judul_clean}
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.04]"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center" style={{ color: theme.muted }}>
                          <Newspaper size={32} />
                        </div>
                      )}
                    </div>

                    <div className="flex flex-grow flex-col justify-between gap-4 p-5">
                      <div className="flex flex-col gap-3">
                        <span
                          className="self-start rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                          style={{ background: badge.bg, border: `1px solid ${badge.border}`, color: badge.color }}
                        >
                          {kategori}
                        </span>
                        <h2
                          className="line-clamp-2 text-[0.9375rem] font-semibold leading-snug transition-colors duration-200 group-hover:text-[#95ccdd]"
                          style={{ color: theme.fg }}
                        >
                          {berita.judul_clean}
                        </h2>
                      </div>

                      <div className="flex items-center justify-between gap-3 pt-3" style={{ borderTop: `1px solid ${theme.divider}` }}>
                        <span className="flex items-center gap-1.5 text-xs" style={{ color: theme.muted }}>
                          <Clock size={11} />
                          {formatDate(berita.waktu_scraping)}
                        </span>
                        <span className="flex items-center gap-1 text-xs font-semibold" style={{ color: theme.blue }}>
                          Baca <ExternalLink size={11} />
                        </span>
                      </div>
                    </div>
                  </article>
                );
              })}
            </section>

            {totalPages > 1 && (
              <nav className="mt-12 flex items-center justify-center gap-2" aria-label="Navigasi halaman berita">
                <button
                  aria-label="Halaman sebelumnya"
                  className="flex h-9 w-9 items-center justify-center rounded-xl border disabled:cursor-not-allowed disabled:opacity-30"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((page) => Math.max(page - 1, 1))}
                  style={{ background: theme.card, borderColor: theme.border, color: theme.fg }}
                >
                  <ChevronLeft size={16} />
                </button>

                {Array.from({ length: totalPages }, (_, index) => index + 1).map((page) => (
                  <button
                    key={page}
                    aria-label={`Halaman ${page}`}
                    className="h-9 w-9 rounded-xl border text-sm font-semibold"
                    onClick={() => setCurrentPage(page)}
                    style={{
                      background: currentPage === page ? theme.blue : theme.card,
                      borderColor: currentPage === page ? theme.blue : theme.border,
                      color: currentPage === page ? "#ffffff" : theme.muted,
                    }}
                  >
                    {page}
                  </button>
                ))}

                <button
                  aria-label="Halaman berikutnya"
                  className="flex h-9 w-9 items-center justify-center rounded-xl border disabled:cursor-not-allowed disabled:opacity-30"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((page) => Math.min(page + 1, totalPages))}
                  style={{ background: theme.card, borderColor: theme.border, color: theme.fg }}
                >
                  <ChevronRight size={16} />
                </button>
              </nav>
            )}
          </>
        )}
      </main>

      <footer className="mt-auto border-t" style={{ borderColor: theme.border }}>
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-xs sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p style={{ color: theme.muted }}>
            (c) {new Date().getFullYear()} Praktikum Data Scraping - S1 Sistem Informasi STIKOM PGRI Banyuwangi
          </p>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1" style={{ color: theme.muted }}>
            <span>
              1124102181{" "}
              <a href="https://github.com/ijeny" target="_blank" rel="noopener noreferrer" style={{ color: theme.fgSub }}>
                Imtinan Jeny M.B.
              </a>
            </span>
            <span style={{ color: theme.divider }}>|</span>
            <span>
              1124102166{" "}
              <a href="https://github.com/hivicode" target="_blank" rel="noopener noreferrer" style={{ color: theme.fgSub }}>
                Bintang Fathir F.A.
              </a>
            </span>
          </div>
        </div>
      </footer>

      {selectedBerita && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4"
          onClick={() => setSelectedBerita(null)}
          style={{
            background: dark ? "rgba(5,8,18,0.8)" : "rgba(20,30,60,0.5)",
            backdropFilter: "blur(10px)",
          }}
        >
          <div
            className="max-h-[92vh] w-full overflow-hidden overflow-y-auto rounded-t-3xl sm:max-w-xl sm:rounded-2xl"
            onClick={(event) => event.stopPropagation()}
            style={{ background: theme.card, border: `1px solid ${theme.border}` }}
          >
            <div className="relative h-52 w-full flex-shrink-0 sm:h-60" style={{ background: dark ? "#1a2540" : "#daeef0" }}>
              {getImageUrl(selectedBerita.url_gambar) ? (
                <img
                  src={getImageUrl(selectedBerita.url_gambar) ?? ""}
                  alt={selectedBerita.judul_asli}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center" style={{ color: theme.muted }}>
                  <Newspaper size={36} />
                </div>
              )}
              <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${theme.card} 0%, transparent 55%)` }} />
              <button
                aria-label="Tutup detail berita"
                className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full border"
                onClick={() => setSelectedBerita(null)}
                style={{
                  background: dark ? "rgba(11,15,30,0.85)" : "rgba(238,246,246,0.9)",
                  borderColor: theme.border,
                  color: theme.fg,
                }}
              >
                <X size={14} />
              </button>
            </div>

            <div className="p-5 sm:p-6">
              <h2 className="mb-3 text-xl font-bold leading-snug" style={{ color: theme.fg }}>
                {selectedBerita.judul_asli}
              </h2>
              <p className="mb-5 flex items-center gap-1.5 text-xs" style={{ color: theme.muted }}>
                <Clock size={11} />
                {formatDateTime(selectedBerita.waktu_scraping)}
              </p>
              {selectedBerita.isi_berita && (
                <p className="mb-6 text-sm leading-relaxed" style={{ color: dark ? "#a8c4d8" : "#3a5070" }}>
                  {selectedBerita.isi_berita}
                </p>
              )}
              <a
                className="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold"
                href={selectedBerita.url_link}
                rel="noopener noreferrer"
                target="_blank"
                style={{ background: theme.blue, color: "#ffffff" }}
              >
                Buka Sumber Asli <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
