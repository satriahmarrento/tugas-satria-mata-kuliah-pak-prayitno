# CampusCare

CampusCare adalah aplikasi untuk melaporkan kerusakan fasilitas kampus.
Aplikasi ini dibuat untuk Tugas Besar PBO dengan Python OOP dan SQLite.

## Fitur

- Register mahasiswa dan petugas
- Login mahasiswa dan petugas
- Mahasiswa membuat laporan kerusakan fasilitas
- Mahasiswa bisa upload foto kerusakan atau mengisi foto path manual
- Mahasiswa melihat laporan miliknya
- Petugas melihat semua laporan
- Petugas mengubah status laporan
- Mahasiswa memberi rating setelah laporan selesai
- Data dummy dibuat otomatis saat pertama kali run
- Tampilan aplikasi memakai Streamlit
- Dashboard ringkasan jumlah laporan berdasarkan status
- Filter dan pencarian laporan

## Struktur File

```text
TUBES/
|-- model.py
|-- database.py
|-- manajer_laporan.py
|-- konfigurasi.py
|-- main_app.py
|-- requirements.txt
|-- uploads/
`-- README.md
```

## Konsep OOP

- Encapsulation: atribut pada class `Laporan` dibuat private.
- Inheritance: `Mahasiswa` dan `Petugas` turunan dari `User`.
- Polymorphism: `StatusBaru`, `StatusDiproses`, dan `StatusSelesai` punya behavior berbeda.
- Abstraction: `Notifikasi` dibuat sebagai interface, lalu dijalankan oleh `NotifikasiConsole`.

## Database

Nama database:

```text
TUBES/campuscare.db
```

Database dibuat otomatis saat aplikasi pertama kali dijalankan.

## Akun Dummy

```text
Mahasiswa:
username: mhs1
password: 123

Mahasiswa:
username: mhs2
password: 123

Petugas:
username: petugas1
password: 123
```

## Cara Menjalankan

Install dependency:

```powershell
pip install -r TUBES\requirements.txt
```

Jalankan:

```powershell
streamlit run TUBES\main_app.py
```

## Catatan

Folder `uploads` akan dibuat otomatis ketika mahasiswa mengupload foto.
Jika tidak ingin upload file, mahasiswa tetap bisa mengisi foto path manual.
