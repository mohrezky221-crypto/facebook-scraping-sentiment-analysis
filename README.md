# Facebook Comment Scraper & Analisis Sentimen (Positif, Negatif, Netral)

Repositori/folder ini berisi kode Python dan dataset hasil scraping serta **Analisis Sentimen 3 Kelas (`Positif`, `Negatif`, `Netral`)** dan **Visualisasi WordCloud** pada komentar media sosial **Facebook** (Postingan Berita Suaradotcom: Isu Foto Gubernur Kaltim Rudy Mas’ud dan Istri di Singapura). Proyek ini dibangun mengikuti struktur proyek referensi teman (`Data Screaping`) dengan penyempurnaan analisis sentimen berbahasa Indonesia.

---

## 📌 Studi Kasus Target
- **Platform**: Facebook
- **Tautan Target**: [https://www.facebook.com/100064500378237/posts/1628147096011954/?app=fbl](https://www.facebook.com/100064500378237/posts/1628147096011954/?app=fbl)
- **Sumber Media**: Suaradotcom
- **Topik Isu**: Sorotan warganet terhadap foto viral Gubernur Kaltim Rudy Mas'ud bersama istri saat berada di Singapura.
- **Tujuan**: Menarik opini publik, membersihkan teks, mengklasifikasikan komentar ke dalam kategori **Positif**, **Negatif**, atau **Netral**, serta memvisualisasikan persepsi publik menggunakan **WordCloud**.

---

## 📁 Struktur Folder Proyek

```text
TUGAS SCRAPING 2/
│
├── Data Screaping/                     # Folder proyek referensi teman (YouTube)
│   └── Data Screaping/
│       ├── youtube_comment_scraper.py
│       ├── youtube_comment_scraper.ipynb
│       └── youtube_comments_sentiment_dataset.csv
│
└── Facebook Scraping/                  # Folder proyek baru Anda (Facebook + Sentimen)
    ├── lexicon/                         # Kamus Leksikon Sentimen Bahasa Indonesia
    │   ├── positive.tsv                 # InSet positive lexicon (3.600+ kata)
    │   └── negative.tsv                 # InSet negative lexicon (6.600+ kata)
    ├── facebook_comment_scraper.py      # Skrip Python utama (Scraping & Analisis Sentimen)
    ├── facebook_comment_scraper.ipynb   # Jupyter Notebook interaktif + Visualisasi WordCloud
    ├── generate_wordcloud.py            # Modul khusus pembuatan gambar WordCloud
    ├── facebook_comments_sentiment_dataset.csv # Dataset hasil scraping & sentimen (260 baris)
    ├── wordcloud_sentiment_comparison.png # Visualisasi WordCloud Positif vs Negatif (300 DPI)
    ├── wordcloud_positif.png            # WordCloud khusus komentar positif
    ├── wordcloud_negatif.png            # WordCloud khusus komentar negatif
    ├── requirements.txt                 # Daftar pustaka (selenium, bs4, pandas, wordcloud)
    └── README.md                        # Dokumentasi teknis & panduan lengkap
```

---

## ⚙️ Metodologi Analisis Sentimen 3 Kelas

Mesin analisis sentimen dirancang khusus untuk teks media sosial bahasa Indonesia:
1. **Leksikon Utama (InSet Lexicon)**:
   - Memuat lebih dari 10.000 kata berbobot polaritas bahasa Indonesia (+1 s.d. +5 untuk positif, -1 s.d. -5 untuk negatif).
2. **Kamus Slang & Kontekstual Media Sosial**:
   - Menangani istilah gaul dan bahasa daerah (*salah pilih, nyungseb, ra nde uteg, sampah, blunder, pamer, hedon, mantap, amanah*).
3. **Penanganan Negasi (*Negation Handling*)**:
   - Kata negasi (*tidak, gak, bukan, kurang, belum, ndak*) otomatis **membalikkan polaritas** kata berikutnya (contoh: *"tidak amanah"* dihitung negatif).
4. **Penanganan Penguat Kata (*Booster Words*)**:
   - Kata penguat (*sangat, banget, sekali, amat, parah*) melipatgandakan bobot intensitas sentimen kata terkait.
5. **Kaidah Penentuan Kelas**:
   - **`Positif`**: `sentiment_score > 0`
   - **`Negatif`**: `sentiment_score < 0`
   - **`Netral`**: `sentiment_score == 0`

---

## 📊 Spesifikasi Kolom Dataset (Data Dictionary)

File dataset `facebook_comments_sentiment_dataset.csv` diekspor dalam format **UTF-8 with BOM (`utf-8-sig`)**:

| Nama Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `post_url` | String | Tautan URL postingan Facebook target |
| `author` | String | Nama akun pengunggah komentar |
| `raw_comment` | String | Teks komentar mentah sebelum diproses |
| `cleaned_comment` | String | Teks komentar setelah sanitasi Regex (bebas link, newline, spasi ganda) |
| `sentiment_label` | String | **Label sentimen 3 kelas: `Positif`, `Negatif`, atau `Netral`** |
| `sentiment_score` | Integer | Skor polaritas numerik sentimen |
| `aspect` | String | Kategori aspek isu publik (*Aspect-Based Rule Hint*) |
| `like_count` | Integer | Jumlah reaksi / like pada komentar |
| `published_time` | String | Waktu relatif pengunggahan (misal: "5 weeks ago") |

---

## 📈 Ringkasan Statistik Hasil Sentimen (260 Komentar)

| Kategori Sentimen | Jumlah Komentar | Persentase | Karakteristik Kata Kunci Utama |
| :--- | :---: | :---: | :--- |
| **Negatif** | **175** | **67.3%** | *gubernur, pejabat, rakyat, salah pilih, kaltim, marwah, sampah, jalan rusak, hedon, nyungseb* |
| **Netral** | **54** | **20.8%** | Pertanyaan faktual, kutipan berita, sebutan nama/panggilan tanpa kata opini. |
| **Positif** | **31** | **11.9%** | *sehat selalu, tugas dinas, alhamdulillah, semangat, pak gub, sukses, amanah* |

---

## 🎨 Visualisasi WordCloud yang Dihasilkan

Visualisasi telah diekspor dalam resolusi tinggi (300 DPI) dan siap disisipkan ke dalam laporan atau presentasi:
1. **[wordcloud_sentiment_comparison.png](file:///c:/Users/kyy/OneDrive/Dokumen/TUGAS%20SCRAPING%202/Facebook%20Scraping/wordcloud_sentiment_comparison.png)**: Tampilan komparasi berdampingan (*Side-by-Side*) antara sentimen Positif (Hijau) dan Negatif (Merah).
2. **[wordcloud_positif.png](file:///c:/Users/kyy/OneDrive/Dokumen/TUGAS%20SCRAPING%202/Facebook%20Scraping/wordcloud_positif.png)**: WordCloud fokus pada opini pendukung dan pembelaan.
3. **[wordcloud_negatif.png](file:///c:/Users/kyy/OneDrive/Dokumen/TUGAS%20SCRAPING%202/Facebook%20Scraping/wordcloud_negatif.png)**: WordCloud fokus pada kritik tajam dan sorotan publik.

---

## 🚀 Cara Menjalankan

### 1. Menjalankan Scraping & Sentimen
```bash
cd "Facebook Scraping"
python facebook_comment_scraper.py
```

### 2. Membuat Ulang WordCloud Saja
```bash
python generate_wordcloud.py
```

### 3. Menjalankan via Jupyter Notebook
```bash
jupyter notebook facebook_comment_scraper.ipynb
```
Jalankan sel 1 hingga 11 untuk melihat alur scraping, tabel dataset, grafik diagram batang/pie chart, dan visualisasi WordCloud secara interaktif.
