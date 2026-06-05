from pathlib import Path


DB_PATH = str(Path(__file__).parent / "campuscare.db")

STATUS_BARU = "Baru"
STATUS_DIPROSES = "Diproses"
STATUS_SELESAI = "Selesai"

PERAN_MAHASISWA = "mahasiswa"
PERAN_PETUGAS = "petugas"

DATA_USER_DUMMY = [
    ("mhs1", "123", "Budi Santoso", PERAN_MAHASISWA),
    ("mhs2", "123", "Siti Aminah", PERAN_MAHASISWA),
    ("petugas1", "123", "Pak Andi", PERAN_PETUGAS),
]

DATA_LAPORAN_DUMMY = [
    (1, "Gedung A Lantai 2", "Lampu lorong mati", "foto/lampu_mati.jpg", STATUS_BARU, None),
    (2, "Laboratorium Komputer", "AC tidak dingin", "foto/ac_rusak.jpg", STATUS_DIPROSES, None),
    (1, "Perpustakaan", "Kursi baca patah", "foto/kursi_patah.jpg", STATUS_SELESAI, 5),
]
