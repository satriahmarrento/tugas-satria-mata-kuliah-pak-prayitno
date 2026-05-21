# main_app.py
import streamlit as st
import datetime
import pandas as pd
import locale

try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        print("Locale id_ID/Indonesian tidak tersedia.")

def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")

try:
    from model import Transaksi
    from manajer_anggaran import AnggaranHarian
    from konfigurasi import KATEGORI_PENGELUARAN # Ambil list kategori
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file.py lain ada.")
    st.stop()

st.set_page_config(page_title="Catatan Pengeluaran", layout="wide", initial_sidebar_state="expanded")

# --- Inisialisasi Pengelola Anggaran (Gunakan Cache) ---
@st.cache_resource
def get_anggaran_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi AnggaranHarian...")
    return AnggaranHarian() # Ini akan memicu cek DB/Tabel di __init__

anggaran = get_anggaran_manager()

# --- Fungsi Halaman/UI ---
def halaman_input(anggaran: AnggaranHarian):
    st.header("Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*", placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*:", KATEGORI_PENGELUARAN, index=0)
        col3, col4 = st.columns([1, 1])
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:", min_value=0.01, step=1000.0, format="%.0f", value=None, placeholder="Contoh: 25000")
        with col4:
            tanggal = st.date_input("Tanggal*:", value=datetime.date.today())
        submitted = st.form_submit_button("Simpan Transaksi")
        if submitted:
            if not deskripsi:
                st.warning("Deskripsi wajib!", icon="⚠️")
            elif jumlah is None or jumlah <= 0:
                st.warning("Jumlah wajib!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(deskripsi, float(jumlah), kategori, tanggal)
                    if anggaran.tambah_transaksi(tx):
                        st.success(f"OK! Simpan.", icon="✅")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Gagal simpan.", icon="❌")

def halaman_riwayat(anggaran: AnggaranHarian):
    st.subheader("Detail Semua Transaksi")
    if st.button("Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()
    with st.spinner("Memuat riwayat..."):
        df_transaksi = anggaran.get_dataframe_transaksi()
    if df_transaksi is None:
        st.error("Gagal ambil riwayat.")
    elif df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_transaksi, use_container_width=True, hide_index=True)

def halaman_ringkasan(anggaran: AnggaranHarian):
    st.subheader("Ringkasan Pengeluaran")
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal"],
                                       key="filter_periode", on_change=lambda: st.cache_data.clear())
    tanggal_filter = None
    label_periode = "(Semua Waktu)"

    # Lanjutin logic ringkasan di sini sesuai Jobsheet...

def main():
    st.sidebar.title("Menu")
    halaman = st.sidebar.radio("Pilih Halaman", ["Input Transaksi", "Riwayat", "Ringkasan"])

    if halaman == "Input Transaksi":
        halaman_input(anggaran)
    elif halaman == "Riwayat":
        halaman_riwayat(anggaran)
    elif halaman == "Ringkasan":
        halaman_ringkasan(anggaran)

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")

if __name__ == "__main__":
    main()