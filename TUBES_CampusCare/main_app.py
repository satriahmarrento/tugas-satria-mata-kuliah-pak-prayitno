from datetime import datetime
from pathlib import Path

import streamlit as st

from konfigurasi import (
    PERAN_MAHASISWA,
    PERAN_PETUGAS,
    STATUS_BARU,
    STATUS_DIPROSES,
    STATUS_SELESAI,
)
from database import Database
from manajer_laporan import ManajerLaporan
from model import Mahasiswa, Petugas


UPLOAD_DIR = Path(__file__).parent / "uploads"
DAFTAR_STATUS = [STATUS_BARU, STATUS_DIPROSES, STATUS_SELESAI]


def setup_aplikasi():
    if "database" not in st.session_state:
        st.session_state.database = Database()
        st.session_state.database.inisialisasi_database()
        st.session_state.manajer_laporan = ManajerLaporan(st.session_state.database)
    if "user_aktif" not in st.session_state:
        st.session_state.user_aktif = None


def buat_user(data_user):
    # Inheritance: object dibuat sesuai peran user.
    if data_user["peran"] == PERAN_MAHASISWA:
        return Mahasiswa(
            data_user["id_user"],
            data_user["username"],
            data_user["nama"],
            data_user["peran"],
        )
    return Petugas(
        data_user["id_user"],
        data_user["username"],
        data_user["nama"],
        data_user["peran"],
    )


def warna_status(status):
    if status == STATUS_BARU:
        return "#2563eb"
    if status == STATUS_DIPROSES:
        return "#d97706"
    return "#16a34a"


def tampil_badge_status(status):
    warna = warna_status(status)
    st.markdown(
        f"""
        <span style="
            background:{warna};
            color:white;
            padding:4px 10px;
            border-radius:6px;
            font-size:14px;
            font-weight:600;
        ">{status}</span>
        """,
        unsafe_allow_html=True,
    )


def simpan_file_upload(file_upload):
    if file_upload is None:
        return ""

    UPLOAD_DIR.mkdir(exist_ok=True)
    waktu = datetime.now().strftime("%Y%m%d%H%M%S")
    nama_file = f"{waktu}_{file_upload.name.replace(' ', '_')}"
    path_file = UPLOAD_DIR / nama_file
    path_file.write_bytes(file_upload.getbuffer())
    return str(Path("uploads") / nama_file)


def hitung_ringkasan(laporan_list):
    rating_list = [
        laporan.rating for laporan in laporan_list if laporan.rating is not None
    ]
    rata_rating = "-"
    if rating_list:
        rata_rating = round(sum(rating_list) / len(rating_list), 1)

    return {
        "total": len(laporan_list),
        STATUS_BARU: len([l for l in laporan_list if l.status.nama == STATUS_BARU]),
        STATUS_DIPROSES: len(
            [l for l in laporan_list if l.status.nama == STATUS_DIPROSES]
        ),
        STATUS_SELESAI: len(
            [l for l in laporan_list if l.status.nama == STATUS_SELESAI]
        ),
        "rating": rata_rating,
    }


def tampil_metrik_laporan(laporan_list):
    ringkasan = hitung_ringkasan(laporan_list)
    kolom1, kolom2, kolom3, kolom4, kolom5 = st.columns(5)
    kolom1.metric("Total", ringkasan["total"])
    kolom2.metric("Baru", ringkasan[STATUS_BARU])
    kolom3.metric("Diproses", ringkasan[STATUS_DIPROSES])
    kolom4.metric("Selesai", ringkasan[STATUS_SELESAI])
    kolom5.metric("Rata Rating", ringkasan["rating"])


def data_laporan_tabel(laporan_list):
    data = []
    for laporan in laporan_list:
        data.append(
            {
                "ID": laporan.id_laporan,
                "Mahasiswa": laporan.nama_mahasiswa,
                "Lokasi": laporan.lokasi,
                "Deskripsi": laporan.deskripsi,
                "Foto": laporan.foto_path,
                "Status": laporan.status.nama,
                "Rating": laporan.rating if laporan.rating is not None else "-",
                "Dibuat": laporan.dibuat_pada,
            }
        )
    return data


def filter_laporan(laporan_list, status_filter, kata_kunci):
    hasil = laporan_list
    if status_filter != "Semua":
        hasil = [laporan for laporan in hasil if laporan.status.nama == status_filter]

    kata_kunci = kata_kunci.strip().lower()
    if kata_kunci:
        hasil = [
            laporan
            for laporan in hasil
            if kata_kunci in laporan.lokasi.lower()
            or kata_kunci in laporan.deskripsi.lower()
            or kata_kunci in laporan.nama_mahasiswa.lower()
        ]
    return hasil


def tampil_tabel_dan_detail(laporan_list, key_prefix):
    if not laporan_list:
        st.info("Belum ada laporan.")
        return

    kolom_filter1, kolom_filter2 = st.columns([1, 2])
    status_filter = kolom_filter1.selectbox(
        "Filter status",
        ["Semua"] + DAFTAR_STATUS,
        key=f"{key_prefix}_status_filter",
    )
    kata_kunci = kolom_filter2.text_input(
        "Cari laporan",
        placeholder="Cari lokasi, deskripsi, atau nama mahasiswa",
        key=f"{key_prefix}_cari",
    )

    laporan_filter = filter_laporan(laporan_list, status_filter, kata_kunci)
    st.dataframe(data_laporan_tabel(laporan_filter), use_container_width=True)

    if not laporan_filter:
        st.info("Tidak ada laporan yang cocok.")
        return

    pilihan = st.selectbox(
        "Detail laporan",
        laporan_filter,
        format_func=lambda laporan: f"{laporan.id_laporan} - {laporan.lokasi}",
        key=f"{key_prefix}_detail",
    )
    tampil_detail_laporan(pilihan)


def tampil_detail_laporan(laporan):
    with st.expander("Lihat detail", expanded=True):
        kolom1, kolom2 = st.columns([2, 1])
        with kolom1:
            st.write(f"ID Laporan: {laporan.id_laporan}")
            st.write(f"Mahasiswa: {laporan.nama_mahasiswa}")
            st.write(f"Lokasi: {laporan.lokasi}")
            st.write(f"Deskripsi: {laporan.deskripsi}")
            st.write(f"Dibuat pada: {laporan.dibuat_pada}")
            st.write("Status:")
            tampil_badge_status(laporan.status.nama)
            st.caption(laporan.status.pesan())
            st.write(f"Rating: {laporan.rating if laporan.rating is not None else '-'}")

        with kolom2:
            st.write("Foto")
            path_foto = Path(__file__).parent / laporan.foto_path
            if laporan.foto_path and path_foto.exists():
                st.image(str(path_foto), use_container_width=True)
            else:
                st.info(laporan.foto_path or "Tidak ada foto.")


def halaman_login():
    st.subheader("Login")
    with st.form("form_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        tombol_login = st.form_submit_button("Login")

    if tombol_login:
        data_user = st.session_state.database.ambil_user_login(username, password)
        if data_user is None:
            st.error("Login gagal.")
            return

        st.session_state.user_aktif = buat_user(data_user)
        st.success("Login berhasil.")
        st.rerun()


def halaman_register():
    st.subheader("Register")
    with st.form("form_register"):
        nama = st.text_input("Nama lengkap")
        username = st.text_input("Username baru")
        password = st.text_input("Password baru", type="password")
        peran = st.selectbox("Peran", [PERAN_MAHASISWA, PERAN_PETUGAS])
        tombol_register = st.form_submit_button("Register")

    if tombol_register:
        if not nama.strip() or not username.strip() or not password.strip():
            st.error("Nama, username, dan password wajib diisi.")
            return
        if st.session_state.database.username_sudah_ada(username):
            st.error("Username sudah dipakai.")
            return

        id_user = st.session_state.database.tambah_user(
            username.strip(),
            password.strip(),
            nama.strip(),
            peran,
        )
        if id_user is None:
            st.error("Register gagal.")
            return

        st.success(f"Register berhasil. ID user: {id_user}. Silakan login.")


def halaman_awal():
    st.title("CampusCare")
    st.write("Sistem Lapor Kerusakan Fasilitas Kampus")
    st.info("Akun dummy: mhs1/123, mhs2/123, petugas1/123")

    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login:
        halaman_login()
    with tab_register:
        halaman_register()


def menu_sidebar():
    user = st.session_state.user_aktif
    st.sidebar.title("CampusCare")
    st.sidebar.write(user.info())
    st.sidebar.caption("Tugas Besar PBO")

    if st.sidebar.button("Logout"):
        st.session_state.user_aktif = None
        st.rerun()


def halaman_mahasiswa():
    user = st.session_state.user_aktif
    manajer = st.session_state.manajer_laporan
    laporan_saya = manajer.lihat_laporan_mahasiswa(user.id_user)

    menu_sidebar()
    st.title("Dashboard Mahasiswa")
    tampil_metrik_laporan(laporan_saya)

    tab_dashboard, tab_buat, tab_laporan, tab_rating = st.tabs(
        ["Ringkasan", "Buat Laporan", "Laporan Saya", "Rating"]
    )

    with tab_dashboard:
        st.subheader("Ringkasan Laporan Saya")
        tampil_tabel_dan_detail(laporan_saya, "mhs_ringkasan")

    with tab_buat:
        st.subheader("Buat Laporan Kerusakan")
        with st.form("form_laporan"):
            lokasi = st.text_input("Lokasi")
            deskripsi = st.text_area("Deskripsi")
            file_upload = st.file_uploader(
                "Upload foto kerusakan",
                type=["jpg", "jpeg", "png"],
            )
            foto_path_manual = st.text_input(
                "Foto path manual",
                placeholder="Contoh: foto/lampu_mati.jpg",
            )
            tombol_simpan = st.form_submit_button("Simpan Laporan")

        if tombol_simpan:
            try:
                foto_path = simpan_file_upload(file_upload) or foto_path_manual
                id_laporan = user.buat_laporan(
                    manajer,
                    lokasi,
                    deskripsi,
                    foto_path,
                )
                st.success(f"Laporan berhasil dibuat. ID laporan: {id_laporan}")
            except ValueError as error:
                st.error(str(error))

    with tab_laporan:
        st.subheader("Laporan Saya")
        tampil_tabel_dan_detail(laporan_saya, "mhs_laporan")

    with tab_rating:
        st.subheader("Beri Rating Laporan Selesai")
        laporan_selesai = [
            laporan for laporan in laporan_saya if laporan.status.nama == STATUS_SELESAI
        ]

        if not laporan_selesai:
            st.info("Belum ada laporan selesai.")
        else:
            with st.form("form_rating"):
                pilihan = st.selectbox(
                    "Pilih laporan",
                    laporan_selesai,
                    format_func=lambda laporan: (
                        f"{laporan.id_laporan} - {laporan.lokasi}"
                    ),
                )
                rating = st.slider("Rating", 1, 5, 5)
                tombol_rating = st.form_submit_button("Simpan Rating")

            if tombol_rating:
                try:
                    manajer.simpan_rating(pilihan.id_laporan, rating)
                    st.success("Rating berhasil disimpan.")
                except ValueError as error:
                    st.error(str(error))


def halaman_petugas():
    user = st.session_state.user_aktif
    manajer = st.session_state.manajer_laporan
    laporan_list = manajer.lihat_semua_laporan()

    menu_sidebar()
    st.title("Dashboard Petugas")
    tampil_metrik_laporan(laporan_list)

    tab_dashboard, tab_laporan, tab_update = st.tabs(
        ["Ringkasan", "Semua Laporan", "Update Status"]
    )

    with tab_dashboard:
        st.subheader("Ringkasan Semua Laporan")
        tampil_tabel_dan_detail(laporan_list, "petugas_ringkasan")

    with tab_laporan:
        st.subheader("Semua Laporan")
        tampil_tabel_dan_detail(laporan_list, "petugas_laporan")

    with tab_update:
        st.subheader("Update Status Laporan")
        if not laporan_list:
            st.info("Belum ada laporan.")
            return

        with st.form("form_update_status"):
            pilihan = st.selectbox(
                "Pilih laporan",
                laporan_list,
                format_func=lambda laporan: (
                    f"{laporan.id_laporan} - {laporan.lokasi}"
                    f" ({laporan.status.nama})"
                ),
            )
            st.write("Status sekarang:")
            tampil_badge_status(pilihan.status.nama)
            status_baru = st.selectbox(
                "Status baru",
                DAFTAR_STATUS,
                index=DAFTAR_STATUS.index(pilihan.status.nama),
            )
            tombol_update = st.form_submit_button("Update Status")

        if tombol_update:
            try:
                user.update_status_laporan(
                    manajer,
                    pilihan.id_laporan,
                    status_baru,
                )
                st.success("Status berhasil diupdate.")
            except ValueError as error:
                st.error(str(error))


def main():
    st.set_page_config(page_title="CampusCare", layout="wide")
    setup_aplikasi()

    user = st.session_state.user_aktif
    if user is None:
        halaman_awal()
    elif user.peran == PERAN_MAHASISWA:
        halaman_mahasiswa()
    elif user.peran == PERAN_PETUGAS:
        halaman_petugas()


if __name__ == "__main__":
    main()

