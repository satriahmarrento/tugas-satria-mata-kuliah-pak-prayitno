from konfigurasi import STATUS_BARU, STATUS_DIPROSES, STATUS_SELESAI
from model import Laporan, NotifikasiConsole, buat_status_laporan


class ManajerLaporan:
    def __init__(self, database, notifikasi=None):
        self.database = database
        self.notifikasi = notifikasi or NotifikasiConsole()

    def tambah_laporan(self, id_mahasiswa, lokasi, deskripsi, foto_path):
        if not lokasi.strip() or not deskripsi.strip() or not foto_path.strip():
            raise ValueError("Lokasi, deskripsi, dan foto path wajib diisi.")

        id_laporan = self.database.tambah_laporan(
            id_mahasiswa,
            lokasi.strip(),
            deskripsi.strip(),
            foto_path.strip(),
            STATUS_BARU,
        )
        self.notifikasi.kirim("petugas", f"Laporan baru dibuat dengan ID {id_laporan}.")
        return id_laporan

    def lihat_semua_laporan(self):
        return [self._baris_ke_laporan(baris) for baris in self.database.ambil_semua_laporan()]

    def lihat_laporan_mahasiswa(self, id_mahasiswa):
        return [
            self._baris_ke_laporan(baris)
            for baris in self.database.ambil_laporan_mahasiswa(id_mahasiswa)
        ]

    def cari_laporan(self, id_laporan):
        baris = self.database.ambil_laporan_by_id(id_laporan)
        if baris is None:
            return None
        return self._baris_ke_laporan(baris)

    def update_status(self, id_laporan, status_baru):
        self._validasi_status(status_baru)
        laporan = self.cari_laporan(id_laporan)
        if laporan is None:
            raise ValueError("Laporan tidak ditemukan.")

        berhasil = self.database.update_status_laporan(id_laporan, status_baru)
        if berhasil:
            status = buat_status_laporan(status_baru)
            self.notifikasi.kirim(
                laporan.nama_mahasiswa,
                f"Status laporan ID {id_laporan} menjadi {status.nama}. {status.pesan()}",
            )
        return berhasil

    def simpan_rating(self, id_laporan, rating):
        laporan = self.cari_laporan(id_laporan)
        if laporan is None:
            raise ValueError("Laporan tidak ditemukan.")

        laporan.beri_rating(rating)
        berhasil = self.database.simpan_rating(id_laporan, rating)
        if berhasil:
            self.notifikasi.kirim(
                "petugas",
                f"Laporan ID {id_laporan} mendapat rating {rating}.",
            )
        return berhasil

    def hapus_laporan(self, id_laporan, id_user, peran):
        from konfigurasi import PERAN_MAHASISWA, STATUS_BARU
        laporan = self.cari_laporan(id_laporan)
        if laporan is None:
            raise ValueError("Laporan tidak ditemukan.")

        if peran == PERAN_MAHASISWA:
            if laporan.id_mahasiswa != id_user:
                raise ValueError("Anda tidak berhak menghapus laporan ini.")
            if laporan.status.nama != STATUS_BARU:
                raise ValueError("Laporan yang sedang diproses atau selesai tidak bisa dibatalkan.")

        berhasil = self.database.hapus_laporan(id_laporan)
        if berhasil:
            self.notifikasi.kirim(
                "petugas",
                f"Laporan ID {id_laporan} di lokasi {laporan.lokasi} telah dibatalkan oleh {laporan.nama_mahasiswa}.",
            )
        return berhasil


    def _validasi_status(self, status_baru):
        if status_baru not in (STATUS_BARU, STATUS_DIPROSES, STATUS_SELESAI):
            raise ValueError("Status tidak valid.")

    def _baris_ke_laporan(self, baris):
        return Laporan(
            id_laporan=baris["id_laporan"],
            id_mahasiswa=baris["id_mahasiswa"],
            nama_mahasiswa=baris["nama_mahasiswa"],
            lokasi=baris["lokasi"],
            deskripsi=baris["deskripsi"],
            foto_path=baris["foto_path"],
            status=baris["status"],
            rating=baris["rating"],
            dibuat_pada=baris["dibuat_pada"],
        )

