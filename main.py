import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import csv
import datetime
import os
import sys
import winsound
import config
from database import load_data, save_data

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MacaEcoCashApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Maca Eco Cash — Dashboard Info")
        self.geometry("520x760") # Ukuran pas agar scroll aktif muncul
        self.configure(fg_color=config.BG_MAIN)

        self.manager = FinanceManager()
        self.current_filter_jenis = "Semua"
        self.current_filter_periode = "Semua Waktu"
        self.filtered_indices = []
        self.toast_timer = None
        self.is_dark_mode = False

        self.anim_masuk_curr = 0
        self.anim_keluar_curr = 0
        self.anim_timer = None

        self.bind("<Return>", lambda event: self.submit("Masuk"))

        # --- KONTAINER UTAMA SCROLLABLE (WAJIB FILL & EXPAND) ---
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_scroll.pack(fill="both", expand=True)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FinanceManager:
    def __init__(self):
        data = load_data()
        self.saldo = data.get("saldo", 0)
        self.transaksi = data.get("transaksi", [])

    def tambah_transaksi(self, keterangan, nominal, jenis, kategori="Lainnya"):
        if jenis == "Masuk":
            self.saldo += nominal
        elif jenis == "Keluar":
            if nominal > self.saldo:
                return False, "Saldo Eco Cash Box tidak mencukupi!"
            self.saldo -= nominal

        now = datetime.datetime.now()
        item = {
            "ket": keterangan,
            "nominal": nominal,
            "jenis": jenis,
            "kategori": kategori,
            "tanggal": now.strftime("%d %b %Y"),
            "waktu_iso": now.isoformat()
        }
        self.transaksi.insert(0, item)
        self.simpan()
        return True, "Transaksi berhasil dicatat."

    def edit_transaksi(self, index_asli, ket_baru, nom_baru, jenis_baru, kat_baru):
        if 0 <= index_asli < len(self.transaksi):
            item_lama = self.transaksi[index_asli]
            
            if item_lama["jenis"] == "Masuk":
                self.saldo -= item_lama["nominal"]
            else:
                self.saldo += item_lama["nominal"]

            if jenis_baru == "Keluar" and nom_baru > self.saldo:
                if item_lama["jenis"] == "Masuk":
                    self.saldo += item_lama["nominal"]
                else:
                    self.saldo -= item_lama["nominal"]
                return False, "Gagal Edit: Saldo tidak mencukupi untuk pengeluaran baru!"

            if jenis_baru == "Masuk":
                self.saldo += nom_baru
            else:
                self.saldo -= nom_baru

            self.transaksi[index_asli]["ket"] = ket_baru
            self.transaksi[index_asli]["nominal"] = nom_baru
            self.transaksi[index_asli]["jenis"] = jenis_baru
            self.transaksi[index_asli]["kategori"] = kat_baru

            self.simpan()
            return True, "Transaksi berhasil diperbarui."
        return False, "Transaksi tidak ditemukan."

    def hapus_transaksi(self, index_asli):
        if 0 <= index_asli < len(self.transaksi):
            item = self.transaksi.pop(index_asli)
            if item["jenis"] == "Masuk":
                self.saldo -= item["nominal"]
            else:
                self.saldo += item["nominal"]
            
            if self.saldo < 0:
                self.saldo = 0

            self.simpan()
            return True, "Transaksi berhasil dihapus."
        return False, "Pilih transaksi terlebih dahulu."

    def simpan(self):
        save_data({
            "saldo": self.saldo,
            "transaksi": self.transaksi
        })

    def filter_transaksi(self, jenis_filter="Semua", periode_filter="Semua Waktu", query_cari=""):
        now = datetime.datetime.now()
        hasil = []
        indices = []

        for idx, item in enumerate(self.transaksi):
            tgl_item = None
            if "waktu_iso" in item:
                try:
                    tgl_item = datetime.datetime.fromisoformat(item["waktu_iso"])
                except ValueError:
                    pass
            
            if not tgl_item:
                try:
                    tgl_item = datetime.datetime.strptime(item["tanggal"], "%d %b %Y")
                except ValueError:
                    tgl_item = now

            pass_periode = False
            if periode_filter == "Semua Waktu":
                pass_periode = True
            elif periode_filter == "Minggu Ini":
                pass_periode = (now - tgl_item).days <= 7
            elif periode_filter == "Bulan Ini":
                pass_periode = (tgl_item.month == now.month) and (tgl_item.year == now.year)
            elif periode_filter == "Tahun Ini":
                pass_periode = (tgl_item.year == now.year)

            pass_jenis = (jenis_filter == "Semua") or (item["jenis"] == jenis_filter)

            pass_cari = True
            if query_cari:
                q = query_cari.lower()
                ket = item.get("ket", "").lower()
                kat = item.get("kategori", "").lower()
                pass_cari = (q in ket) or (q in kat)

            if pass_periode and pass_jenis and pass_cari:
                hasil.append(item)
                indices.append(idx)

        return hasil, indices


class MacaEcoCashApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Maca Eco Cash — Dashboard Info")
        self.geometry("520x820")
        self.configure(fg_color=config.BG_MAIN)

        self.manager = FinanceManager()
        self.current_filter_jenis = "Semua"
        self.current_filter_periode = "Semua Waktu"
        self.filtered_indices = []
        self.toast_timer = None
        self.is_dark_mode = False

        self.anim_masuk_curr = 0
        self.anim_keluar_curr = 0
        self.anim_timer = None

        self.bind("<Return>", lambda event: self.submit("Masuk"))

        # --- KONTAINER UTAMA SCROLLABLE ---
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_scroll.pack(fill="both", expand=True)

        # --- HEADER UTAMA ---
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent", corner_radius=0)
        self.header_frame.pack(fill="x", pady=(15, 8), padx=12)

        self.top_header_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.top_header_box.pack(fill="x")

        self.right_action_box = ctk.CTkFrame(self.top_header_box, fg_color="transparent")
        self.right_action_box.pack(side="right", anchor="ne")

        self.btn_help = ctk.CTkButton(self.right_action_box, text="?", width=36, height=36, font=("Helvetica", 14, "bold"), fg_color=config.ACCENT_GOLD, text_color="#0F172A", corner_radius=18, command=self.buka_pusat_bantuan)
        self.btn_help.pack(side="right", padx=(8, 0))

        self.btn_theme = ctk.CTkButton(self.right_action_box, text="Dark Mode", width=100, height=36, font=("Helvetica", 12, "bold"), fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", corner_radius=18, command=self.toggle_theme)
        self.btn_theme.pack(side="right")

        self.left_brand_box = ctk.CTkFrame(self.top_header_box, fg_color="transparent")
        self.left_brand_box.pack(side="left", anchor="w")

        self.load_header_logo_besar()

        self.left_title_box = ctk.CTkFrame(self.left_brand_box, fg_color="transparent")
        self.left_title_box.pack(side="left", padx=(12, 0), anchor="w")

        self.lbl_sub = ctk.CTkLabel(self.left_title_box, text="MACA EXPO • LITERASI KEUANGAN", font=("Helvetica", 11, "bold"), text_color=config.ACCENT_GOLD)
        self.lbl_sub.pack(anchor="w")

        self.lbl_title = ctk.CTkLabel(self.left_title_box, text="Maca Eco Cash", font=("Helvetica", 20, "bold"), text_color=config.TEXT_PRIMARY)
        self.lbl_title.pack(anchor="w", pady=(2, 0))

        # --- NOTIFIKASI TOAST ---
        self.lbl_notif = ctk.CTkLabel(self.main_scroll, text="", font=("Helvetica", 12, "bold"), fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", corner_radius=8, height=32)

        # --- KARTU METRIK SALDO ---
        self.card_frame = ctk.CTkFrame(self.main_scroll, fg_color=config.BG_CARD, corner_radius=16, border_width=1, border_color=config.BORDER_COLOR)
        self.card_frame.pack(fill="x", padx=12, pady=8)

        self.lbl_tag = ctk.CTkLabel(self.card_frame, text="TOTAL SALDO AKTIF", font=("Helvetica", 12, "bold"), text_color=config.TEXT_MUTED)
        self.lbl_tag.pack(anchor="w", padx=18, pady=(14, 0))

        self.lbl_saldo = ctk.CTkLabel(self.card_frame, text="Rp 0", font=("Helvetica", 32, "bold"), text_color=config.TEXT_PRIMARY)
        self.lbl_saldo.pack(anchor="w", padx=18, pady=(2, 16))

        # --- GRAFIK ARUS KAS ---
        self.chart_frame = ctk.CTkFrame(self.main_scroll, fg_color=config.BG_CARD, corner_radius=16, border_width=1, border_color=config.BORDER_COLOR)
        self.chart_frame.pack(fill="x", padx=12, pady=8)

        self.lbl_chart_title = ctk.CTkLabel(self.chart_frame, text="Ringkasan Arus Kas", font=("Helvetica", 13, "bold"), text_color=config.TEXT_PRIMARY)
        self.lbl_chart_title.pack(anchor="w", padx=18, pady=(12, 0))

        import tkinter as tk
        self.canvas = tk.Canvas(self.chart_frame, height=58, highlightthickness=0, bd=0)
        self.canvas.pack(fill="x", padx=18, pady=8)

        # --- FORM INPUT TRANSAKSI ---
        self.form_frame = ctk.CTkFrame(self.main_scroll, fg_color=config.BG_CARD, corner_radius=16, border_width=1, border_color=config.BORDER_COLOR)
        self.form_frame.pack(fill="x", padx=12, pady=8)

        self.cmb_kategori = ctk.CTkOptionMenu(
            self.form_frame,
            values=config.KATEGORI_TRANSAKSI,
            font=("Helvetica", 12, "bold"),
            fg_color=config.BG_MAIN,
            text_color=config.TEXT_PRIMARY,
            button_color=config.ACCENT_BLUE,
            height=38,
            corner_radius=10
        )
        self.cmb_kategori.pack(fill="x", padx=16, pady=(14, 8))

        self.ent_ket = ctk.CTkEntry(self.form_frame, placeholder_text="Keterangan (Contoh: Uang Saku)", font=("Helvetica", 12), fg_color=config.BG_MAIN, text_color=config.TEXT_PRIMARY, border_color=config.BORDER_COLOR, corner_radius=10, height=40)
        self.ent_ket.pack(fill="x", padx=16, pady=(0, 8))

        self.ent_nom = ctk.CTkEntry(self.form_frame, placeholder_text="Nominal (Contoh: 20000)", font=("Helvetica", 12), fg_color=config.BG_MAIN, text_color=config.TEXT_PRIMARY, border_color=config.BORDER_COLOR, corner_radius=10, height=40)
        self.ent_nom.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.btn_box.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_masuk = ctk.CTkButton(self.btn_box, text="+ Pemasukan", fg_color=config.COLOR_INCOME, text_color="#FFFFFF", font=("Helvetica", 12, "bold"), corner_radius=10, height=40, command=lambda: self.submit("Masuk"))
        self.btn_masuk.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_keluar = ctk.CTkButton(self.btn_box, text="- Pengeluaran", fg_color=config.COLOR_EXPENSE, text_color="#FFFFFF", font=("Helvetica", 12, "bold"), corner_radius=10, height=40, command=lambda: self.submit("Keluar"))
        self.btn_keluar.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # --- PANEL RIWAYAT TRANSAKSI ---
        self.history_frame = ctk.CTkFrame(self.main_scroll, fg_color=config.BG_CARD, corner_radius=16, border_width=1, border_color=config.BORDER_COLOR)
        self.history_frame.pack(fill="x", padx=12, pady=8)

        self.hist_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.hist_header.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_hist = ctk.CTkLabel(self.hist_header, text="Riwayat Transaksi", font=("Helvetica", 13, "bold"), text_color=config.TEXT_PRIMARY)
        self.lbl_hist.pack(side="left")

        self.btn_export_csv = ctk.CTkButton(self.hist_header, text="CSV", fg_color=config.ACCENT_GOLD, text_color="#0F172A", font=("Helvetica", 11, "bold"), corner_radius=8, width=50, height=30, command=self.export_csv)
        self.btn_export_csv.pack(side="right", padx=(6, 0))

        self.btn_export_pdf = ctk.CTkButton(self.hist_header, text="PDF", fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", font=("Helvetica", 11, "bold"), corner_radius=8, width=50, height=30, command=self.export_pdf)
        self.btn_export_pdf.pack(side="right")

        self.ent_search = ctk.CTkEntry(self.history_frame, placeholder_text="Cari transaksi / kategori...", font=("Helvetica", 11), fg_color=config.BG_MAIN, text_color=config.TEXT_PRIMARY, border_color=config.BORDER_COLOR, corner_radius=8, height=32)
        self.ent_search.pack(fill="x", padx=16, pady=(2, 6))
        self.ent_search.bind("<KeyRelease>", lambda event: self.refresh_ui())

        self.filter_time_box = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.filter_time_box.pack(fill="x", padx=16, pady=(2, 6))

        self.lbl_time_tag = ctk.CTkLabel(self.filter_time_box, text="Periode:", font=("Helvetica", 11, "bold"), text_color=config.TEXT_MUTED)
        self.lbl_time_tag.pack(side="left", padx=(0, 8))

        self.cmb_periode = ctk.CTkOptionMenu(
            self.filter_time_box,
            values=["Semua Waktu", "Minggu Ini", "Bulan Ini", "Tahun Ini"],
            font=("Helvetica", 11, "bold"),
            fg_color=config.BG_MAIN,
            text_color=config.TEXT_PRIMARY,
            button_color=config.ACCENT_BLUE,
            height=30,
            corner_radius=8,
            command=self.set_periode_filter
        )
        self.cmb_periode.pack(side="left", fill="x", expand=True)

        self.filter_jenis_box = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.filter_jenis_box.pack(fill="x", padx=16, pady=(0, 8))

        self.btn_f_semua = ctk.CTkButton(self.filter_jenis_box, text="Semua", fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", font=("Helvetica", 11, "bold"), corner_radius=8, height=30, command=lambda: self.set_jenis_filter("Semua"))
        self.btn_f_semua.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_f_masuk = ctk.CTkButton(self.filter_jenis_box, text="Masuk", fg_color=config.BG_MAIN, text_color=config.TEXT_PRIMARY, font=("Helvetica", 11, "bold"), corner_radius=8, height=30, command=lambda: self.set_jenis_filter("Masuk"))
        self.btn_f_masuk.pack(side="left", expand=True, fill="x", padx=(4, 4))

        self.btn_f_keluar = ctk.CTkButton(self.filter_jenis_box, text="Keluar", fg_color=config.BG_MAIN, text_color=config.TEXT_PRIMARY, font=("Helvetica", 11, "bold"), corner_radius=8, height=30, command=lambda: self.set_jenis_filter("Keluar"))
        self.btn_f_keluar.pack(side="left", expand=True, fill="x", padx=(4, 0))

        self.listbox = tk.Listbox(self.history_frame, font=("Helvetica", 11), bd=0, highlightthickness=0, height=6)
        self.listbox.pack(fill="x", padx=16, pady=(2, 8))
        self.listbox.bind("<<ListboxSelect>>", self.on_select_item)

        # TOMBOL AKSI EDIT & HAPUS
        self.action_item_box = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.action_item_box.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_edit = ctk.CTkButton(self.action_item_box, text="Edit Terpilih", fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", font=("Helvetica", 11, "bold"), corner_radius=8, height=32, command=self.buka_dialog_edit, state="disabled")
        self.btn_edit.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_hapus = ctk.CTkButton(self.action_item_box, text="Hapus Terpilih", fg_color=config.COLOR_EXPENSE, text_color="#FFFFFF", font=("Helvetica", 11, "bold"), corner_radius=8, height=32, command=self.hapus_terpilih, state="disabled")
        self.btn_hapus.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # --- FOOTER COPYRIGHT ---
        self.footer_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent", corner_radius=0, height=34)
        self.footer_frame.pack(fill="x", pady=(12, 18))

        self.lbl_copyright = ctk.CTkLabel(self.footer_frame, text="© 2026 Nafi Alzena Nugroho - Vectorius", font=("Helvetica", 10), text_color=config.TEXT_MUTED)
        self.lbl_copyright.pack(anchor="center")

        self.update_colors_theme()
        self.refresh_ui()

    def toggle_theme(self):
        if self.is_dark_mode:
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="Dark Mode")
            self.is_dark_mode = False
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="Light Mode")
            self.is_dark_mode = True

        self.update_colors_theme()
        self.refresh_ui()

    def update_colors_theme(self):
        if self.is_dark_mode:
            bg_list = config.BG_MAIN[1]
            fg_list = config.TEXT_PRIMARY[1]
            bg_card = config.BG_CARD[1]
        else:
            bg_list = config.BG_MAIN[0]
            fg_list = config.TEXT_PRIMARY[0]
            bg_card = config.BG_CARD[0]

        self.listbox.configure(bg=bg_list, fg=fg_list, selectbackground=config.ACCENT_BLUE[1] if self.is_dark_mode else config.ACCENT_BLUE[0])
        self.canvas.configure(bg=bg_card)

    def load_header_logo_besar(self):
        logos = [config.LOGO_KIRI_HEADER, config.LOGO_KANAN_HEADER]
        for logo_file in logos:
            logo_path = resource_path(logo_file)
            if os.path.exists(logo_path):
                try:
                    img_raw = Image.open(logo_path)
                    img_resized = img_raw.resize((52, 52), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img_resized)
                    
                    if not hasattr(self, "logo_besar_refs"):
                        self.logo_besar_refs = []
                    self.logo_besar_refs.append(img_tk)

                    lbl_img = ctk.CTkLabel(self.left_brand_box, text="", image=img_tk)
                    lbl_img.pack(side="left", padx=(0, 8), anchor="c")
                except Exception as e:
                    print(f"Gagal memuat logo {logo_path}: {e}")

    def play_sound(self):
        audio_path = resource_path(config.AUDIO_EFEK)
        if os.path.exists(audio_path):
            try:
                winsound.PlaySound(audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Gagal memutar audio: {e}")

    def buka_pusat_bantuan(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Pusat Bantuan - Maca Eco Cash")
        help_window.geometry("400x340")
        help_window.configure(fg_color=config.BG_MAIN)
        help_window.attributes("-topmost", True)

        lbl_head = ctk.CTkLabel(help_window, text="PUSAT BANTUAN", font=("Helvetica", 14, "bold"), text_color=config.ACCENT_GOLD)
        lbl_head.pack(pady=(16, 6))

        txt_box = ctk.CTkTextbox(help_window, font=("Helvetica", 11), fg_color=config.BG_CARD, text_color=config.TEXT_PRIMARY, corner_radius=10)
        txt_box.pack(fill="both", expand=True, padx=16, pady=(6, 16))
        txt_box.insert("0.0", config.PANDUAN_APLIKASI.strip())
        txt_box.configure(state="disabled")

    def show_notification(self, pesan):
        if self.toast_timer:
            self.after_cancel(self.toast_timer)
            
        self.lbl_notif.configure(text=pesan)
        self.lbl_notif.pack(after=self.top_header_box, fill="x", padx=12, pady=(0, 6))
        
        self.toast_timer = self.after(2000, lambda: self.lbl_notif.pack_forget())

    def on_select_item(self, event):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            self.btn_edit.configure(state="normal")
            self.btn_hapus.configure(state="normal")
        else:
            self.btn_edit.configure(state="disabled")
            self.btn_hapus.configure(state="disabled")

    def buka_dialog_edit(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            return

        listbox_index = selected_indices[0]
        real_index = self.filtered_indices[listbox_index]
        item = self.manager.transaksi[real_index]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Transaksi")
        dialog.geometry("380x340")
        dialog.configure(fg_color=config.BG_MAIN)
        dialog.attributes("-topmost", True)

        lbl = ctk.CTkLabel(dialog, text="EDIT TRANSAKSI", font=("Helvetica", 13, "bold"), text_color=config.ACCENT_GOLD)
        lbl.pack(pady=(16, 8))

        cmb_kat = ctk.CTkOptionMenu(dialog, values=config.KATEGORI_TRANSAKSI, font=("Helvetica", 11, "bold"), fg_color=config.BG_CARD, text_color=config.TEXT_PRIMARY, button_color=config.ACCENT_BLUE, height=34)
        cmb_kat.pack(fill="x", padx=18, pady=6)
        cmb_kat.set(item.get("kategori", "Lainnya"))

        ent_ket = ctk.CTkEntry(dialog, font=("Helvetica", 11), fg_color=config.BG_CARD, text_color=config.TEXT_PRIMARY, height=36)
        ent_ket.pack(fill="x", padx=18, pady=6)
        ent_ket.insert(0, item["ket"])

        ent_nom = ctk.CTkEntry(dialog, font=("Helvetica", 11), fg_color=config.BG_CARD, text_color=config.TEXT_PRIMARY, height=36)
        ent_nom.pack(fill="x", padx=18, pady=6)
        ent_nom.insert(0, str(item["nominal"]))

        cmb_jns = ctk.CTkOptionMenu(dialog, values=["Masuk", "Keluar"], font=("Helvetica", 11, "bold"), fg_color=config.BG_CARD, text_color=config.TEXT_PRIMARY, button_color=config.ACCENT_BLUE, height=34)
        cmb_jns.pack(fill="x", padx=18, pady=6)
        cmb_jns.set(item["jenis"])

        def simpan_perubahan():
            ket_b = ent_ket.get().strip()
            nom_raw = ent_nom.get().strip()
            jns_b = cmb_jns.get()
            kat_b = cmb_kat.get()

            if not ket_b or not nom_raw:
                messagebox.showwarning("Input Kosong", "Isi keterangan dan nominal terlebih dahulu.")
                return

            try:
                nom_b = int(nom_raw)
                if nom_b <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Format Salah", "Nominal harus berupa angka bulat positif.")
                return

            sukses, pesan = self.manager.edit_transaksi(real_index, ket_b, nom_b, jns_b, kat_b)
            if not sukses:
                messagebox.showerror("Gagal", pesan)
                return

            self.show_notification(pesan)
            self.refresh_ui()
            dialog.destroy()

        btn_save = ctk.CTkButton(dialog, text="Simpan Perubahan", fg_color=config.ACCENT_BLUE, text_color="#FFFFFF", font=("Helvetica", 11, "bold"), height=36, command=simpan_perubahan)
        btn_save.pack(pady=14)

    def set_jenis_filter(self, jenis):
        self.current_filter_jenis = jenis
        active_col = config.ACCENT_BLUE
        inactive_col = config.BG_MAIN
        
        self.btn_f_semua.configure(fg_color=active_col if jenis == "Semua" else inactive_col, text_color="#FFFFFF" if jenis == "Semua" else config.TEXT_PRIMARY)
        self.btn_f_masuk.configure(fg_color=active_col if jenis == "Masuk" else inactive_col, text_color="#FFFFFF" if jenis == "Masuk" else config.TEXT_PRIMARY)
        self.btn_f_keluar.configure(fg_color=active_col if jenis == "Keluar" else inactive_col, text_color="#FFFFFF" if jenis == "Keluar" else config.TEXT_PRIMARY)
        
        self.refresh_ui()

    def set_periode_filter(self, periode):
        self.current_filter_periode = periode
        self.refresh_ui()

    def submit(self, jenis):
        ket = self.ent_ket.get().strip()
        nom_raw = self.ent_nom.get().strip()
        kat = self.cmb_kategori.get()

        if not ket or not nom_raw:
            messagebox.showwarning("Input Kosong", "Isi keterangan dan nominal terlebih dahulu.")
            return

        try:
            nom = int(nom_raw)
            if nom <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Format Salah", "Nominal harus berupa angka bulat positif.")
            return

        sukses, pesan = self.manager.tambah_transaksi(ket, nom, jenis, kat)
        if not sukses:
            messagebox.showerror("Gagal", pesan)
            return

        self.play_sound()
        self.show_notification(pesan)
        self.refresh_ui()
        self.ent_ket.delete(0, len(self.ent_ket.get()))
        self.ent_nom.delete(0, len(self.ent_nom.get()))

    def hapus_terpilih(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            return

        listbox_index = selected_indices[0]
        real_index = self.filtered_indices[listbox_index]

        sukses, pesan = self.manager.hapus_transaksi(real_index)
        if sukses:
            self.show_notification(pesan)
            self.refresh_ui()

    def export_csv(self):
        q = self.ent_search.get().strip() if hasattr(self, 'ent_search') else ""
        filtered_data, _ = self.manager.filter_transaksi(self.current_filter_jenis, self.current_filter_periode, q)
        if not filtered_data:
            messagebox.showwarning("Kosong", "Tidak ada data transaksi yang cocok untuk diexport!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"Laporan_Keuangan_{self.current_filter_periode.replace(' ', '_')}.csv"
        )
        
        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Tanggal", "Kategori", "Jenis Transaksi", "Keterangan", "Nominal (Rp)"])
                    for item in filtered_data:
                        writer.writerow([item.get("tanggal", "-"), item.get("kategori", "Lainnya"), item["jenis"], item["ket"], item["nominal"]])
                self.show_notification("Laporan CSV berhasil diunduh.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan file: {e}")

    def export_pdf(self):
        q = self.ent_search.get().strip() if hasattr(self, 'ent_search') else ""
        filtered_data, _ = self.manager.filter_transaksi(self.current_filter_jenis, self.current_filter_periode, q)
        if not filtered_data:
            messagebox.showwarning("Kosong", "Tidak ada data transaksi yang cocok untuk diexport!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile=f"Laporan_Keuangan_{self.current_filter_periode.replace(' ', '_')}.pdf"
        )

        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=4)
            subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748B'), alignment=1, spaceAfter=12)

            elements.append(Paragraph("MACA ECO CASH", title_style))
            elements.append(Paragraph(f"Laporan Transaksi — Periode: {self.current_filter_periode}", subtitle_style))
            elements.append(Spacer(1, 10))

            tot_masuk = sum(i["nominal"] for i in filtered_data if i["jenis"] == "Masuk")
            tot_keluar = sum(i["nominal"] for i in filtered_data if i["jenis"] == "Keluar")

            summary_data = [
                ["Filter Periode", "Total Pemasukan", "Total Pengeluaran"],
                [self.current_filter_periode, f"Rp {tot_masuk:,}", f"Rp {tot_keluar:,}"]
            ]
            summary_table = Table(summary_data, colWidths=[170, 170, 170])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 15))

            table_data = [["No", "Tanggal", "Kategori", "Jenis", "Keterangan", "Nominal (Rp)"]]
            for idx, item in enumerate(filtered_data, 1):
                table_data.append([
                    str(idx),
                    item.get("tanggal", "-"),
                    item.get("kategori", "Lainnya"),
                    item["jenis"],
                    item["ket"],
                    f"Rp {item['nominal']:,}"
                ])

            table = Table(table_data, colWidths=[25, 75, 90, 55, 140, 125])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ALIGN', (5,0), (5,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(table)

            doc.build(elements)
            self.show_notification("Laporan PDF berhasil dicetak.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat file PDF: {e}")

    def animate_chart(self, target_masuk, target_keluar):
        if self.anim_timer:
            self.after_cancel(self.anim_timer)

        diff_masuk = target_masuk - self.anim_masuk_curr
        diff_keluar = target_keluar - self.anim_keluar_curr

        if abs(diff_masuk) < 1 and abs(diff_keluar) < 1:
            self.anim_masuk_curr = target_masuk
            self.anim_keluar_curr = target_keluar
            self.render_canvas(self.anim_masuk_curr, self.anim_keluar_curr, target_masuk, target_keluar)
            return

        self.anim_masuk_curr += diff_masuk * 0.25
        self.anim_keluar_curr += diff_keluar * 0.25

        self.render_canvas(self.anim_masuk_curr, self.anim_keluar_curr, target_masuk, target_keluar)
        self.anim_timer = self.after(16, lambda: self.animate_chart(target_masuk, target_keluar))

    def render_canvas(self, val_masuk, val_keluar, target_masuk, target_keluar):
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 380

        max_val = max(target_masuk, target_keluar, 1)
        max_bar_width = max(canvas_width - 150, 50)

        width_masuk = int((val_masuk / max_val) * max_bar_width) if max_val > 0 else 0
        width_keluar = int((val_keluar / max_val) * max_bar_width) if max_val > 0 else 0

        text_col = config.TEXT_PRIMARY[1] if self.is_dark_mode else config.TEXT_PRIMARY[0]
        income_col = config.COLOR_INCOME[1] if self.is_dark_mode else config.COLOR_INCOME[0]
        expense_col = config.COLOR_EXPENSE[1] if self.is_dark_mode else config.COLOR_EXPENSE[0]

        self.canvas.create_text(8, 12, anchor="w", text="Masuk:", fill=text_col, font=("Helvetica", 10, "bold"))
        self.canvas.create_rectangle(70, 6, 70 + max(width_masuk, 4), 18, fill=income_col, outline="")
        self.canvas.create_text(80 + max(width_masuk, 4), 12, anchor="w", text=f"Rp {target_masuk:,}", fill=income_col, font=("Helvetica", 10, "bold"))

        self.canvas.create_text(8, 40, anchor="w", text="Keluar:", fill=text_col, font=("Helvetica", 10, "bold"))
        self.canvas.create_rectangle(70, 34, 70 + max(width_keluar, 4), 46, fill=expense_col, outline="")
        self.canvas.create_text(80 + max(width_keluar, 4), 40, anchor="w", text=f"Rp {target_keluar:,}", fill=expense_col, font=("Helvetica", 10, "bold"))

    def refresh_ui(self):
        # Jika transaksi kosong, pastikan saldo tetap aman di 0
        if not self.manager.transaksi:
            self.manager.saldo = 0

        self.lbl_saldo.configure(text=f"Rp {self.manager.saldo:,}")

        q = self.ent_search.get().strip() if hasattr(self, 'ent_search') else ""
        filtered_data, indices = self.manager.filter_transaksi(self.current_filter_jenis, self.current_filter_periode, q)
        
        # Jika data filter kosong, set total ke 0 agar tidak error/bug
        tot_masuk = sum(i["nominal"] for i in filtered_data if i["jenis"] == "Masuk") if filtered_data else 0
        tot_keluar = sum(i["nominal"] for i in filtered_data if i["jenis"] == "Keluar") if filtered_data else 0
        
        self.animate_chart(tot_masuk, tot_keluar)

        self.btn_edit.configure(state="disabled")
        self.btn_hapus.configure(state="disabled")

        self.listbox.delete(0, "end")
        self.filtered_indices = indices

        if not filtered_data:
            self.listbox.insert("end", " (Belum ada riwayat transaksi)")
        else:
            for item in filtered_data:
                tgl = item.get("tanggal", "-")
                kat = item.get("kategori", "Lainnya")
                simbol = "[+]" if item["jenis"] == "Masuk" else "[-]"
                teks = f" {tgl}  |  [{kat}] {simbol} {item['ket']} — Rp {item['nominal']:,}"
                self.listbox.insert("end", teks)

if __name__ == "__main__":
    app = MacaEcoCashApp()
    app.mainloop()