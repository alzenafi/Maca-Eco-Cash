import streamlit as st
import datetime
import os
import csv
from database import load_data, save_data

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Maca Eco Cash - Literasi Keuangan",
    page_icon="💰",
    layout="centered"
)

# Judul dan Header ala Website Modern
st.title("🌱 Maca Eco Cash")
st.markdown("### Maca Expo • Literasi Keuangan")
st.write("Keuanganku, Hasil Cerdas Literasiku")
st.markdown("---")

# Memuat Data Keuangan
data = load_data()
saldo = data.get("saldo", 0)
transaksi = data.get("transaksi", [])

# Tampilan Saldo Utama (Card Style)
st.metric(label="TOTAL SALDO ECO CASH BOX", value=f"Rp {saldo:,}")
st.markdown("---")

# Bagian Form Input Transaksi
st.subheader("➕ Tambah Transaksi Baru")
with st.form("form_transaksi"):
    keterangan = st.text_input("Keterangan Transaksi", placeholder="Contoh: Tabungan Harian / Jajan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    col1, col2 = st.columns(2)
    with col1:
        submit_masuk = st.form_submit_button("Pemasukan (+)")
    with col2:
        submit_keluar = st.form_submit_button("Pengeluaran (-)")

    if submit_masuk or submit_keluar:
        jenis = "Masuk" if submit_masuk else "Keluar"
        
        if not keterangan.strip():
            st.warning("Mohon isi keterangan transaksi terlebih dahulu!")
        elif nominal <= 0:
            st.warning("Nominal harus lebih besar dari 0!")
        elif jenis == "Keluar" and nominal > saldo:
            st.error("Saldo Eco Cash Box tidak mencukupi!")
        else:
            if jenis == "Masuk":
                saldo += nominal
            else:
                saldo -= nominal

            item = {
                "ket": keterangan,
                "nominal": nominal,
                "jenis": jenis,
                "tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            transaksi.insert(0, item)
            save_data({"saldo": saldo, "transaksi": transaksi})
            st.success("Transaksi berhasil dicatat!")
            st.rerun()

# Bagian Riwayat Transaksi & Filter
st.markdown("---")
st.subheader("📜 Riwayat Transaksi")

filter_opsi = st.selectbox("Filter Tampilan", ["Semua", "Masuk", "Keluar"])

# Filter data
filtered_transaksi = [
    item for item in transaksi 
    if filter_opsi == "Semua" or item["jenis"] == filter_opsi
]

if not filtered_transaksi:
    st.info("Belum ada riwayat transaksi.")
else:
    for idx, item in enumerate(filtered_transaksi):
        simbol = "🟢 [+]" if item["jenis"] == "Masuk" else "🔴 [-]"
        st.write(f"{simbol} **{item['ket']}** — Rp {item['nominal']:,} *({item['tanggal']})*")

# Copyright Footer Web
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2026 Nafi Alzena Nugroho - Vectorius</p>", unsafe_allow_html=True)