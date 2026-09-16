# GrowMatch

## Deskripsi Aplikasi

**GrowMatch** adalah aplikasi web bertema **Urban Farming & Biodiversity** yang membantu pengguna menemukan tanaman yang sesuai dengan kondisi lingkungan dan kemampuan perawatannya. Pengguna dapat memasukkan lokasi tempat tinggal, jenis ruang (indoor atau outdoor), frekuensi penyiraman yang dapat dilakukan, serta tingkat pengalaman dalam merawat tanaman.

Berdasarkan informasi tersebut, GrowMatch akan menganalisis kondisi pengguna dan memberikan **rekomendasi tanaman yang sesuai**, sehingga pengguna dapat memilih tanaman yang lebih sesuai dengan lingkungan dan kemampuan perawatannya.


## Anggota Kelompok

1. **2506609132 - Aisyah Zayyana Hanifah**
2. **2506657094 - Muhammad Nararya Ardhana**
3. **2506590920 - Deodatus Kevin Sihaloho**
4. **2506540670 - Kaysan Salman Ali Kusumah**
5. **2506611856 - Leow Vincent Vintizel**


## Daftar Modul Rencana

### 1. Homepage

Menjadi halaman utama GrowMatch yang memperkenalkan aplikasi, menjelaskan cara kerja GrowMatch, dan menyediakan akses ke fitur-fitur utama.

**PIC:** Leow Vincent Vintizel

### 2. Profile Page & Authentication

Mengelola akun dan profil pengguna, termasuk register, login, logout, serta pengelolaan informasi profil.

**PIC:** Muhammad Nararya Ardhana

### 3. Plant Catalog

Menyediakan katalog tanaman yang dapat dilihat detail tanaman beserta informasi perawatannya oleh pengguna.

**PIC:** Aisyah Zayyana Hanifah

### 4. Plant Recommendation

Memberikan rekomendasi tanaman berdasarkan kondisi dan preferensi yang dimasukkan oleh pengguna, seperti lokasi tempat tinggal dan frekuensi penyiraman.

**PIC:** Deodatus Kevin Sihaloho

### 5. My Garden & Care Log

Memungkinkan pengguna mengelola tanaman yang dimiliki serta mencatat aktivitas perawatan seperti penyiraman, pemupukan, dan pemangkasan.

**PIC:** Kaysan Salman Ali Kusumah

### 6. Plant Review

Memungkinkan pengguna memberikan rating dan review terhadap tanaman serta melihat review dari pengguna lain.

**PIC:** Leow Vincent Vintizel


## Public API

### 1. Perenual API 

Perenual API digunakan untuk memperoleh data dan karakteristik tanaman yang digunakan dalam Plant Catalog dan sistem rekomendasi.

Dokumentasi: https://www.perenual.com/docs/api 

### 2. Open-Meteo Weather API 

Open-Meteo Weather API digunakan untuk memperoleh data kondisi lingkungan berdasarkan lokasi pengguna yang digunakan dalam proses rekomendasi.

Dokumentasi: https://open-meteo.com/en/docs 


## Peran Pengguna

- **Guest:** Dapat mengakses Homepage dan melihat katalog serta informasi tanaman yang bersifat publik.
- **User:** Dapat menggunakan fitur rekomendasi, mengelola My Garden & Care Log, memberikan review, dan mengelola profil.
- **Admin:** Dapat mengelola data tanaman dan akses admin portal.
