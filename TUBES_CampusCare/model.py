from abc import ABC, abstractmethod
from datetime import datetime

from konfigurasi import STATUS_BARU, STATUS_DIPROSES, STATUS_SELESAI


# Inheritance: Mahasiswa dan Petugas adalah turunan dari User.
class User:
    def __init__(self, id_user, username, nama, peran):
        self.id_user = id_user
        self.username = username
        self.nama = nama
        self.peran = peran

    def info(self):
        return f"{self.nama} ({self.peran})"


class Mahasiswa(User):
    def buat_laporan(self, manajer_laporan, lokasi, deskripsi, foto_path):
        return manajer_laporan.tambah_laporan(self.id_user, lokasi, deskripsi, foto_path)

    def batalkan_laporan(self, manajer_laporan, id_laporan):
        return manajer_laporan.hapus_laporan(id_laporan, self.id_user, self.peran)


class Petugas(User):
    def update_status_laporan(self, manajer_laporan, id_laporan, status_baru):
        return manajer_laporan.update_status(id_laporan, status_baru)


# Polymorphism: setiap status punya warna dan pesan yang berbeda.
class StatusLaporan(ABC):
    nama = ""
    warna = ""

    @abstractmethod
    def pesan(self):
        pass

    def tampil(self):
        reset = "\033[0m"
        return f"{self.warna}{self.nama}{reset}"

    def bisa_diberi_rating(self):
        return False


class StatusBaru(StatusLaporan):
    nama = STATUS_BARU
    warna = "\033[94m"

    def pesan(self):
        return "Laporan baru masuk dan menunggu petugas."


class StatusDiproses(StatusLaporan):
    nama = STATUS_DIPROSES
    warna = "\033[93m"

    def pesan(self):
        return "Laporan sedang ditangani petugas."


class StatusSelesai(StatusLaporan):
    nama = STATUS_SELESAI
    warna = "\033[92m"

    def pesan(self):
        return "Laporan sudah selesai ditangani."

    def bisa_diberi_rating(self):
        return True


def buat_status_laporan(nama_status):
    daftar_status = {
        STATUS_BARU: StatusBaru,
        STATUS_DIPROSES: StatusDiproses,
        STATUS_SELESAI: StatusSelesai,
    }
    kelas_status = daftar_status.get(nama_status, StatusBaru)
    return kelas_status()


# Abstraction: Notifikasi dibuat sebagai interface sederhana.
class Notifikasi(ABC):
    @abstractmethod
    def kirim(self, penerima, pesan):
        pass


class NotifikasiConsole(Notifikasi):
    def kirim(self, penerima, pesan):
        print(f"[NOTIFIKASI] Untuk {penerima}: {pesan}")


class NotifikasiToast(Notifikasi):
    def kirim(self, penerima, pesan):
        import streamlit as st
        # 1. Tampilkan live toast
        try:
            st.toast(f"🔔 {pesan}")
        except Exception:
            pass
        # 2. Simpan di session state agar bisa dibaca di dashboard
        if "notifikasi_list" not in st.session_state:
            st.session_state.notifikasi_list = []
        st.session_state.notifikasi_list.insert(0, {
            "penerima": penerima,
            "pesan": pesan,
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })


class Laporan:
    def __init__(
        self,
        id_laporan,
        id_mahasiswa,
        nama_mahasiswa,
        lokasi,
        deskripsi,
        foto_path,
        status,
        rating=None,
        dibuat_pada=None,
    ):
        # Encapsulation: atribut laporan dibuat private.
        self.__id_laporan = id_laporan
        self.__id_mahasiswa = id_mahasiswa
        self.__nama_mahasiswa = nama_mahasiswa
        self.__lokasi = lokasi
        self.__deskripsi = deskripsi
        self.__foto_path = foto_path
        self.__status = buat_status_laporan(status)
        self.__rating = rating
        self.__dibuat_pada = dibuat_pada or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id_laporan(self):
        return self.__id_laporan

    @property
    def id_mahasiswa(self):
        return self.__id_mahasiswa

    @property
    def nama_mahasiswa(self):
        return self.__nama_mahasiswa

    @property
    def lokasi(self):
        return self.__lokasi

    @property
    def deskripsi(self):
        return self.__deskripsi

    @property
    def foto_path(self):
        return self.__foto_path

    @property
    def status(self):
        return self.__status

    @property
    def rating(self):
        return self.__rating

    @property
    def dibuat_pada(self):
        return self.__dibuat_pada

    def ubah_status(self, status_baru):
        self.__status = buat_status_laporan(status_baru)

    def beri_rating(self, rating):
        if not self.__status.bisa_diberi_rating():
            raise ValueError("Rating hanya bisa diberikan untuk laporan selesai.")
        if rating < 1 or rating > 5:
            raise ValueError("Rating harus 1 sampai 5.")
        self.__rating = rating

    def ringkasan(self):
        nilai_rating = self.__rating if self.__rating is not None else "-"
        return (
            f"ID: {self.__id_laporan} | "
            f"Mahasiswa: {self.__nama_mahasiswa} | "
            f"Lokasi: {self.__lokasi} | "
            f"Status: {self.__status.tampil()} | "
            f"Rating: {nilai_rating}"
        )

    def detail(self):
        return (
            f"ID Laporan   : {self.__id_laporan}\n"
            f"Mahasiswa    : {self.__nama_mahasiswa}\n"
            f"Lokasi       : {self.__lokasi}\n"
            f"Deskripsi    : {self.__deskripsi}\n"
            f"Foto Path    : {self.__foto_path}\n"
            f"Status       : {self.__status.tampil()}\n"
            f"Info Status  : {self.__status.pesan()}\n"
            f"Rating       : {self.__rating if self.__rating is not None else '-'}\n"
            f"Dibuat Pada  : {self.__dibuat_pada}"
        )
