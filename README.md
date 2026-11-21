# Maca Eco Cash — Spectra Science Club

**Maca Eco Cash** adalah proyek inovasi teknologi dan literasi keuangan yang dikembangkan oleh **Spectra Science Club** untuk ajang **Maca Expo ke-9**. Mengusung tema *"Berliterasi, Untuk Bumi Lestari"*, proyek ini menggabungkan manajemen kas digital berbasis web yang ramah lingkungan (*paperless*) dengan media edukasi interaktif.

---

## Tentang Proyek

Proyek ini terdiri dari dua ekosistem utama yang saling melengkapi:
1. **Maca Eco Cash (Web App Utama):** Aplikasi pencatatan keuangan harian berbasis web untuk mempermudah pengurus organisasi, bendahara kelas, maupun ekstrakurikuler dalam mengelola pemasukan dan pengeluaran secara otomatis, transparan, dan akurat.
2. **Maca Eco Cash: Pixel Adventure (Web Game):** Game *retro platformer* bergaya piksel (dibangun menggunakan Godot Engine dan diekspor ke HTML5) yang dirancang untuk mengenalkan konsep menabung dan kepedulian lingkungan kepada pelajar secara menyenangkan.

---

## Fitur Utama Aplikasi Web

- **Pencatatan Kas Real-Time:** Input pemasukan dan pengeluaran harian dengan kalkulasi saldo otomatis tanpa risiko salah hitung manual.
- **Visualisasi Arus Kas:** Indikator perbandingan dana masuk dan keluar yang mudah dibaca dalam satu dasbor.
- **Desain Adaptif (9:16 & 16:9):** Tata letak responsif yang optimal ditampilkan baik di layar ponsel vertikal maupun layar monitor/TV pameran.
- **Mode Gelap & Terang (Dark/Light Mode):** Kenyamanan visual yang dapat disesuaikan dengan kondisi pencahayaan ruangan.
- **Ekspor Laporan Instan:** Mendukung pengunduhan data riwayat transaksi ke format **CSV** serta pencetakan laporan dalam format **PDF**.
- **Penyimpanan Lokal Aman:** Menggunakan `localStorage` peramban sehingga data transaksi tetap tersimpan meskipun halaman dimuat ulang.

---

## Struktur Direktori

```text
maca-eco-cash/
├── index.html          # Struktur utama antarmuka aplikasi web
├── style.css           # Pengaturan tata letak responsif & tema gelap/terang
├── script.js           # Logika transaksi, penyimpanan lokal, & ekspor CSV/PDF
├── logo-maca-expo.png  # Aset logo resmi Maca Expo ke-9
├── logo-spectra.png    # Aset logo resmi Spectra Science Club
└── README.md           # Dokumentasi proyek
