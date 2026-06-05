import sqlite3

from konfigurasi import DB_PATH, DATA_LAPORAN_DUMMY, DATA_USER_DUMMY


class Database:
    def __init__(self, path_db=DB_PATH):
        self.path_db = path_db

    def koneksi(self):
        conn = sqlite3.connect(self.path_db)
        conn.row_factory = sqlite3.Row
        return conn

    def inisialisasi_database(self):
        with self.koneksi() as conn:
            # Tabel user dipakai untuk login mahasiswa dan petugas.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    nama TEXT NOT NULL,
                    peran TEXT NOT NULL
                )
                """
            )
            # Tabel laporan menyimpan data kerusakan fasilitas kampus.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS laporan (
                    id_laporan INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_mahasiswa INTEGER NOT NULL,
                    lokasi TEXT NOT NULL,
                    deskripsi TEXT NOT NULL,
                    foto_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    rating INTEGER,
                    dibuat_pada TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_mahasiswa) REFERENCES users(id_user)
                )
                """
            )
            conn.commit()
        self._buat_data_dummy_jika_kosong()

    def _buat_data_dummy_jika_kosong(self):
        with self.koneksi() as conn:
            jumlah_user = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if jumlah_user > 0:
                return

            # Data dummy dibuat sekali saat database masih kosong.
            conn.executemany(
                """
                INSERT INTO users (username, password, nama, peran)
                VALUES (?, ?, ?, ?)
                """,
                DATA_USER_DUMMY,
            )
            conn.executemany(
                """
                INSERT INTO laporan
                    (id_mahasiswa, lokasi, deskripsi, foto_path, status, rating)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                DATA_LAPORAN_DUMMY,
            )
            conn.commit()

    def ambil_user_login(self, username, password):
        with self.koneksi() as conn:
            return conn.execute(
                """
                SELECT id_user, username, nama, peran
                FROM users
                WHERE username = ? AND password = ?
                """,
                (username, password),
            ).fetchone()

    def username_sudah_ada(self, username):
        with self.koneksi() as conn:
            data_user = conn.execute(
                "SELECT id_user FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return data_user is not None

    def tambah_user(self, username, password, nama, peran):
        with self.koneksi() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, password, nama, peran)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, password, nama, peran),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def tambah_laporan(self, id_mahasiswa, lokasi, deskripsi, foto_path, status):
        with self.koneksi() as conn:
            cursor = conn.execute(
                """
                INSERT INTO laporan
                    (id_mahasiswa, lokasi, deskripsi, foto_path, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_mahasiswa, lokasi, deskripsi, foto_path, status),
            )
            conn.commit()
            return cursor.lastrowid

    def ambil_semua_laporan(self):
        with self.koneksi() as conn:
            return conn.execute(
                """
                SELECT
                    laporan.id_laporan,
                    laporan.id_mahasiswa,
                    users.nama AS nama_mahasiswa,
                    laporan.lokasi,
                    laporan.deskripsi,
                    laporan.foto_path,
                    laporan.status,
                    laporan.rating,
                    laporan.dibuat_pada
                FROM laporan
                JOIN users ON users.id_user = laporan.id_mahasiswa
                ORDER BY laporan.id_laporan DESC
                """
            ).fetchall()

    def ambil_laporan_mahasiswa(self, id_mahasiswa):
        with self.koneksi() as conn:
            return conn.execute(
                """
                SELECT
                    laporan.id_laporan,
                    laporan.id_mahasiswa,
                    users.nama AS nama_mahasiswa,
                    laporan.lokasi,
                    laporan.deskripsi,
                    laporan.foto_path,
                    laporan.status,
                    laporan.rating,
                    laporan.dibuat_pada
                FROM laporan
                JOIN users ON users.id_user = laporan.id_mahasiswa
                WHERE laporan.id_mahasiswa = ?
                ORDER BY laporan.id_laporan DESC
                """,
                (id_mahasiswa,),
            ).fetchall()

    def ambil_laporan_by_id(self, id_laporan):
        with self.koneksi() as conn:
            return conn.execute(
                """
                SELECT
                    laporan.id_laporan,
                    laporan.id_mahasiswa,
                    users.nama AS nama_mahasiswa,
                    laporan.lokasi,
                    laporan.deskripsi,
                    laporan.foto_path,
                    laporan.status,
                    laporan.rating,
                    laporan.dibuat_pada
                FROM laporan
                JOIN users ON users.id_user = laporan.id_mahasiswa
                WHERE laporan.id_laporan = ?
                """,
                (id_laporan,),
            ).fetchone()

    def update_status_laporan(self, id_laporan, status_baru):
        with self.koneksi() as conn:
            cursor = conn.execute(
                "UPDATE laporan SET status = ? WHERE id_laporan = ?",
                (status_baru, id_laporan),
            )
            conn.commit()
            return cursor.rowcount > 0

    def simpan_rating(self, id_laporan, rating):
        with self.koneksi() as conn:
            cursor = conn.execute(
                "UPDATE laporan SET rating = ? WHERE id_laporan = ?",
                (rating, id_laporan),
            )
            conn.commit()
            return cursor.rowcount > 0
