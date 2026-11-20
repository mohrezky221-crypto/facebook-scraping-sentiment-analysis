"""
================================================================================
MODUL VISUALISASI WORDCLOUD SENTIMEN KOMENTAR FACEBOOK
================================================================================
Fungsi:
1. Menghasilkan visualisasi WordCloud untuk Komentar Positif dan Negatif.
2. Menghapus kata umum / stopwords bahasa Indonesia dan kata slang non-informatif.
3. Menyimpan gambar dalam resolusi tinggi (PNG, 300 DPI):
   - wordcloud_sentiment_comparison.png (Komparasi side-by-side)
   - wordcloud_positif.png
   - wordcloud_negatif.png
================================================================================
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Daftar kata umum / stopwords bahasa Indonesia yang difilter agar tidak mengotori WordCloud
INDONESIAN_STOPWORDS = set([
    "yang", "yg", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "utk", "pada", "dgn", "dengan",
    "adalah", "yaitu", "ada", "tidak", "gak", "ga", "nggak", "tak", "bukan", "karena", "karna",
    "juga", "jg", "hanya", "cuma", "bisa", "akan", "sudah", "udah", "telah", "masih", "lagi", "lgi",
    "saya", "aku", "kami", "kita", "dia", "mereka", "kamu", "anda", "beliau", "beliu",
    "saja", "aja", "kan", "lah", "kah", "pun", "ya", "yah", "sih", "kok", "ko", "nih", "tuh", "dong",
    "kalo", "kalau", "jika", "biar", "supaya", "seperti", "kaya", "kayak", "sama", "sm",
    "jadi", "jd", "bikin", "buat", "oleh", "atas", "bawah", "dalam", "dlm", "luar",
    "mau", "ingin", "harus", "pasti", "tahu", "tau", "tapi", "tp", "namun", "padahal",
    "apa", "siapa", "kapan", "dimana", "kenapa", "mengapa", "bagaimana", "gimana",
    "banget", "bgt", "sekali", "sangat", "amat", "terlalu", "paling", "lebih", "lbih",
    "orang", "org", "para", "hal", "banyak", "bnyk", "semua", "semuanya", "gitu", "gtu",
    "klu", "klo", "dr", "tp", "trs", "trus", "sdh", "udh", "klau", "blm", "belum",
    "nya", "bos", "boss", "mah", "deh", "loh", "eh", "ah", "oh", "pas"
])


def generate_sentiment_wordclouds(csv_filename: str = "facebook_comments_sentiment_dataset.csv"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, csv_filename)

    if not os.path.exists(csv_path):
        print(f"[ERROR] Berkas dataset {csv_path} tidak ditemukan!")
        return

    df = pd.read_csv(csv_path)
    print("Memproses data untuk pembuatan WordCloud...")

    neg_df = df[df["sentiment_label"] == "Negatif"]
    pos_df = df[df["sentiment_label"] == "Positif"]

    neg_text = " ".join(neg_df["cleaned_comment"].dropna().astype(str))
    pos_text = " ".join(pos_df["cleaned_comment"].dropna().astype(str))

    # 1. WordCloud Sentimen Negatif
    wc_neg = WordCloud(
        width=800,
        height=500,
        background_color="white",
        colormap="Reds",
        stopwords=INDONESIAN_STOPWORDS,
        max_words=80
    ).generate(neg_text)

    # 2. WordCloud Sentimen Positif
    wc_pos = WordCloud(
        width=800,
        height=500,
        background_color="white",
        colormap="Greens",
        stopwords=INDONESIAN_STOPWORDS,
        max_words=80
    ).generate(pos_text)

    # Simpan file individual
    neg_file = os.path.join(script_dir, "wordcloud_negatif.png")
    pos_file = os.path.join(script_dir, "wordcloud_positif.png")
    wc_neg.to_file(neg_file)
    wc_pos.to_file(pos_file)

    # 3. Gambar Komparasi Side-by-Side
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor="#f8f9fa")

    axes[0].imshow(wc_pos, interpolation="bilinear")
    axes[0].set_title(
        f"WordCloud Sentimen POSITIF ({len(pos_df)} Komentar)\nKata Kunci Apresiasi / Pembelaan",
        fontsize=13,
        fontweight="bold",
        color="#1e7e34",
        pad=15
    )
    axes[0].axis("off")

    axes[1].imshow(wc_neg, interpolation="bilinear")
    axes[1].set_title(
        f"WordCloud Sentimen NEGATIF ({len(neg_df)} Komentar)\nKata Kunci Kritik / Kekecewaan",
        fontsize=13,
        fontweight="bold",
        color="#c82333",
        pad=15
    )
    axes[1].axis("off")

    plt.suptitle(
        "KOMPARASI WORDCLOUD ANALISIS SENTIMEN KOMENTAR FACEBOOK\n"
        "Studi Kasus: Isu Foto Gubernur Kaltim Rudy Mas'ud di Singapura",
        fontsize=15,
        fontweight="bold",
        y=0.98
    )

    comparison_file = os.path.join(script_dir, "wordcloud_sentiment_comparison.png")
    plt.tight_layout()
    plt.savefig(comparison_file, dpi=300, bbox_inches="tight")
    plt.close()

    print("[SUKSES] Visualisasi WordCloud berhasil disimpan:")
    print(f"  1. Komparasi : {comparison_file}")
    print(f"  2. Positif   : {pos_file}")
    print(f"  3. Negatif   : {neg_file}")


if __name__ == "__main__":
    generate_sentiment_wordclouds()
