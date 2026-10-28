TEXT RPG - QOL UPDATE
=====================

PENTING
-------
Paket ini adalah overlay update untuk repository TextRPG yang sudah ada.
Ekstrak file-file di dalam ZIP ke folder proyek TextRPG kamu dan izinkan
file yang sama (misalnya main.py, engine.py) untuk diganti. Folder stories/
tidak disertakan atau diubah, jadi cerita yang sudah ada tetap aman.

FITUR
-----
1. Warna teks untuk judul, narasi, pilihan, status, hasil dadu, efek, dan battle.
2. Animasi ASCII singkat ketika dadu dilempar. Animasi tidak melakukan roll;
   angka hasil tetap berasal dari random.randint yang sama seperti sebelumnya.
3. Animasi loading singkat saat memilih petualangan.
4. Dukungan ilustrasi ASCII opsional dari folder art/.
5. Tetap bisa berjalan tanpa Rich, tetapi warna/animasi dapat lebih terbatas.

INSTALASI
---------
1. Backup folder proyek terlebih dahulu.
2. Ekstrak isi ZIP ke folder TextRPG, gabungkan folder systems/ dan art/.
3. Buka terminal di folder TextRPG.
4. Pasang dependency yang diperlukan:
      py -m pip install -r requirements.txt
5. Jalankan:
      py main.py

ILUSTRASI DALAM CERITA
----------------------
Sebuah node cerita boleh memiliki field "art" opsional. Contoh:

{
  "text": "Kamu memasuki reruntuhan kuno.",
  "art": "art/demo_ruins.txt",
  "end": true
}

Path ilustrasi harus berada di folder art/. Jika field "art" tidak ada,
cerita akan berjalan seperti biasa. File ilustrasi harus berupa teks UTF-8.
Kamu bisa mengonversi gambar menjadi ASCII melalui https://inascii.com/
atau https://tools.ocmalabs.com/ascii-art-converter/ lalu simpan hasilnya
sebagai .txt di folder art/.

MEMATIKAN ANIMASI
-----------------
PowerShell:
    $env:TEXTRPG_NO_ANIMATION="1"
    py main.py

Untuk mengaktifkan lagi, tutup terminal atau jalankan:
    Remove-Item Env:TEXTRPG_NO_ANIMATION

CATATAN
-------
- Tidak ada perubahan pada aturan dadu, damage, peluang, atribut, maupun efek.
- Animasi otomatis dilewati ketika output bukan terminal interaktif.
- Jika Rich belum dipasang, kode menggunakan fallback terminal.
- Pastikan untuk menggabungkan file ke repository yang ada, bukan menghapus
  folder stories/ yang sudah kamu kumpulkan.
