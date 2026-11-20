"""
================================================================================
FACEBOOK COMMENT SCRAPER & ANALISIS SENTIMEN (POSITIF, NEGATIF, NETRAL)
================================================================================
Studi Kasus:
Postingan Berita Media (Suaradotcom): 
"Gubernur Kalimantan Timur (Kaltim), Rudy Mas'ud, menjadi sorotan setelah foto 
dirinya bersama sang istri, Syarifah Suraidah, saat berada di Singapura viral."
Target Link: https://www.facebook.com/100064500378237/posts/1628147096011954/?app=fbl

Fitur Unggulan:
1. Scraping tanpa Facebook Graph API Token / Developer Account (Browser Automation).
2. Menggunakan Selenium WebDriver & Headless Chrome yang dioptimasi.
3. Otomatisasi penutupan overlay/modal popup login Facebook agar tidak memblokir ekstraksi.
4. Fitur Auto-Scroll & Auto-Expand ("View more comments" dan "View replies").
5. Ekstraksi komprehensif: Author, Waktu Unggah, Jumlah Reaksi/Like, dan Isi Komentar.
6. Preprocessing & Sanitasi Regex:
   - Menghapus tautan/URL website.
   - Menghapus newline berlebih (\\n, \\r), tab (\\t), spasi ganda.
   - Membuang baris kosong atau komentar tanpa teks bermakna (hanya simbol).
7. Aspect-Based Rule-based Hint (Kategori Isu Publik Kaltim).
8. Analisis Sentimen 3 Kelas (Positif, Negatif, Netral):
   - Menggunakan InSet Lexicon (Indonesian Sentiment Lexicon) + Kamus Slang Kontekstual.
   - Penanganan Negasi (kata 'tidak', 'gak', 'bukan' membalik polaritas sentimen).
   - Penanganan Penguat Kata (Booster words seperti 'banget', 'sangat', 'parah').
   - Perhitungan skor polaritas numerik (sentiment_score) dan label (sentiment_label).
9. Ekspor CSV dengan format UTF-8 with BOM ('utf-8-sig') agar kompatibel di Excel & Pandas.
================================================================================
"""

import os
import re
import sys
import time
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

# Pastikan Selenium dan BeautifulSoup terinstall
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"[ERROR] Dependensi belum lengkap: {e}")
    print("Silakan jalankan perintah terminal: pip install selenium beautifulsoup4 pandas")
    sys.exit(1)


# ==============================================================================
# 1. PARAMETER INPUT & KONFIGURASI
# ==============================================================================
# Daftar tautan postingan Facebook yang ingin di-scrape
POST_URLS: List[str] = [
    "https://www.facebook.com/100064500378237/posts/1628147096011954/?app=fbl"
]

# Batas maksimal komentar yang ingin ditarik per postingan (default: 300)
COMMENT_LIMIT_PER_POST: int = 300

# Jumlah iterasi scroll & expand komentar maksimal
MAX_SCROLL_ROUNDS: int = 25

# Mode Headless (True: browser berjalan di latar belakang tanpa jendela fisik)
HEADLESS_MODE: bool = True

# Nama file output dataset CSV
OUTPUT_FILENAME: str = "facebook_comments_sentiment_dataset.csv"


# ==============================================================================
# 2. DEFINISI ASPEK (ASPECT-BASED RULE-BASED HINT)
# ==============================================================================
ASPECT_KEYWORDS: Dict[str, List[str]] = {
    "Gaya Hidup & Plesiran Pejabat": [
        "singapura", "singapore", "liburan", "plesiran", "jalan jalan", "jalan-jalan",
        "shopping", "belanja", "mewah", "hedon", "hedonisme", "pamer", "kaya",
        "noni belanda", "istri", "bini", "cantik", "foto", "senyum", "gaya"
    ],
    "Kinerja & Kebijakan Kaltim": [
        "kaltim", "kalimantan", "kalimantan timur", "samarinda", "balikpapan", "rakyat",
        "masyarakat", "daerah", "anggaran", "apbd", "uang rakyat", "pajak", "banjir",
        "jalan", "rusak", "infrastruktur", "kemiskinan", "tambang", "kinerja", "janji"
    ],
    "Etika, Integritas & Moral Pemimpin": [
        "etika", "moral", "adab", "malu", "pantas", "nggak pantas", "tidak pantas",
        "empati", "amanah", "cerminan", "sampah", "terlalu", "kelakuan", "sadar",
        "pejabat", "contoh", "keteladanan"
    ],
    "Kritik Politik & Pilkada": [
        "gubernur", "pemimpin", "pilkada", "pilih", "salah pilih", "coblos", "suara",
        "partai", "rezim", "dinasti", "nyungseb", "politik", "timses", "kampanye",
        "periode", "jabatan", "mumpung"
    ],
    "Pembelaan & Respon Positif": [
        "tugas", "dinas", "kunjungan", "kerja", "wajar", "hak", "fitnah", "iri",
        "dengki", "semangat", "tenang", "sukses", "hebat", "sehat", "terbaik"
    ]
}


# ==============================================================================
# 3. KAMUS SENTIMEN & LOGIKA ANALISIS SENTIMEN BAHASA INDONESIA
# ==============================================================================
# Kata penegas/pengubah negasi yang membalikkan sentimen kata setelahnya
NEGATION_WORDS = {
    "tidak", "bukan", "gak", "ga", "nggak", "tak", "kurang", "jangan",
    "belom", "belum", "ndak", "gk", "tdk"
}

# Kata penguat (Booster words) yang memperbesar bobot sentimen
BOOSTER_WORDS = {
    "sangat": 1.5, "banget": 1.5, "amat": 1.5, "sekali": 1.5,
    "parah": 1.5, "bgt": 1.5, "bener-bener": 1.5, "beneran": 1.3
}

# Kamus slang & sentimen kontekstual untuk isu politik dan media sosial
SLANG_SENTIMENT_DICT: Dict[str, int] = {
    # Kata / Frasa Negatif
    "salah pilih": -4, "sampah": -5, "gubernur sampah": -5, "nyungseb": -4,
    "digot": -3, "aneh": -3, "ra nde uteg": -5, "ora duwe utek": -5,
    "ga punya otak": -5, "gak punya otak": -5, "tidak punya otak": -5,
    "blunder": -4, "matek": -4, "mampus": -4, "mati": -3, "copot": -4,
    "turunkan": -4, "parah": -4, "koruptor": -5, "korupsi": -5, "hancur": -4,
    "rusak": -3, "ancur": -4, "bobrok": -4, "bego": -4, "goblok": -5,
    "tolol": -5, "bodoh": -4, "hedon": -3, "pamer": -3, "gasss pooll": -2,
    "keblinger": -4, "zalim": -4, "kecewa": -4, "memalukan": -4, "dusta": -4,
    "bohong": -4, "muak": -4, "ngawur": -4, "penipu": -5, "culas": -4,
    # Kata / Frasa Positif
    "semangat": 4, "mantap": 4, "sukses": 4, "terbaik": 4, "bagus": 3,
    "keren": 4, "hebat": 4, "amanah": 4, "sehat selalu": 4, "berprestasi": 4,
    "setuju": 3, "maju": 3, "bangga": 4, "terbukti": 3, "adil": 4,
    "cerdas": 4, "bijak": 4, "sabar": 3, "terpercaya": 4
}


def load_sentiment_lexicon() -> Dict[str, int]:
    """
    Memuat leksikon InSet (Indonesian Sentiment Lexicon) dari folder 'lexicon/'
    jika tersedia, digabungkan dengan kamus slang kontekstual.
    """
    lexicon: Dict[str, int] = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pos_path = os.path.join(base_dir, "lexicon", "positive.tsv")
    neg_path = os.path.join(base_dir, "lexicon", "negative.tsv")

    if os.path.exists(pos_path) and os.path.exists(neg_path):
        try:
            df_pos = pd.read_csv(pos_path, sep="\t")
            for _, r in df_pos.iterrows():
                lexicon[str(r["word"]).strip().lower()] = int(r["weight"])

            df_neg = pd.read_csv(neg_path, sep="\t")
            for _, r in df_neg.iterrows():
                lexicon[str(r["word"]).strip().lower()] = int(r["weight"])
        except Exception as e:
            print(f"  [!] Peringatan: Gagal memuat file InSet lexicon: {e}")

    # Tambahkan kamus kontekstual khusus isu politik/publik
    lexicon.update(SLANG_SENTIMENT_DICT)
    return lexicon


# Muat leksikon ke memori sekali saat skrip diimpor/dijalankan
SENTIMENT_LEXICON = load_sentiment_lexicon()


def analyze_sentiment(text: str) -> Tuple[str, int]:
    """
    Menghitung skor polaritas sentimen kalimat dan mengklasifikasikan ke:
    - 'Positif' (skor > 0)
    - 'Negatif' (skor < 0)
    - 'Netral'  (skor == 0)
    
    Dilengkapi deteksi frasa majemuk, penanganan negasi, dan penguat kata (booster).
    """
    text_lower = str(text).lower()
    score = 0
    matched_phrases = []

    # 1. Cek frasa majemuk multi-kata terlebih dahulu (misal: 'salah pilih', 'ra nde uteg')
    for phrase, wgt in SLANG_SENTIMENT_DICT.items():
        if " " in phrase and phrase in text_lower:
            score += wgt
            matched_phrases.append(phrase)

    # 2. Tokenisasi kata
    words = re.findall(r"\b\w+\b", text_lower)
    i = 0
    while i < len(words):
        w = words[i]

        # Periksa apakah ada kata penguat (booster) di depan kata sentimen
        multiplier = 1.0
        if w in BOOSTER_WORDS and i < len(words) - 1:
            multiplier = BOOSTER_WORDS[w]
            i += 1
            w = words[i]

        # Periksa apakah ada kata negasi di depan kata sentimen
        if w in NEGATION_WORDS and i < len(words) - 1:
            next_w = words[i + 1]
            if next_w in SENTIMENT_LEXICON:
                # Balikkan nilai sentimen jika didahului negasi
                score += int(-SENTIMENT_LEXICON[next_w] * multiplier)
                i += 2
                continue
            i += 1
            continue

        # Cek kata tunggal dalam leksikon (kecuali kata yang sudah masuk frasa majemuk)
        if w in SENTIMENT_LEXICON and w not in " ".join(matched_phrases):
            score += int(SENTIMENT_LEXICON[w] * multiplier)
        i += 1

    # 3. Klasifikasi label 3 kelas
    if score > 0:
        return "Positif", score
    elif score < 0:
        return "Negatif", score
    else:
        return "Netral", score


# ==============================================================================
# 4. FUNGSI PREPROCESSING, PEMBERSIHAN TEKS & HELPER
# ==============================================================================
def parse_like_count(raw_val: Any) -> int:
    """Mengonversi format like/tanggapan ('1.2K', '2M', angka mentah) menjadi integer."""
    if raw_val is None:
        return 0
    if isinstance(raw_val, int):
        return raw_val

    val = str(raw_val).strip().upper()
    if not val or val == "0":
        return 0

    try:
        if val.endswith("K"):
            num = float(val[:-1].replace(",", "."))
            return int(num * 1_000)
        elif val.endswith("M"):
            num = float(val[:-1].replace(",", "."))
            return int(num * 1_000_000)
        elif val.endswith("B"):
            num = float(val[:-1].replace(",", "."))
            return int(num * 1_000_000_000)
        else:
            clean_digits = re.sub(r"[^\d]", "", val)
            return int(clean_digits) if clean_digits else 0
    except (ValueError, TypeError):
        return 0


def clean_comment_text(text: Optional[str]) -> str:
    """Sanitasi teks komentar mentah berbasis Regex (URL, newline, tab, spasi berlebih)."""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_meaningful_comment(text: str) -> bool:
    """Memastikan komentar tidak kosong dan mengandung karakter alfanumerik."""
    if not text:
        return False
    return bool(re.search(r"\w", text, flags=re.UNICODE))


def classify_aspect(text: str) -> str:
    """Kategorisasi aspek berdasarkan pencocokan kata kunci dengan batas kata (\\b)."""
    lower_text = text.lower()
    matched_aspects = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        for kw in keywords:
            escaped_kw = re.escape(kw.lower())
            pattern = rf"\b{escaped_kw}\b"
            if re.search(pattern, lower_text):
                matched_aspects.append(aspect)
                break
    return " | ".join(matched_aspects) if matched_aspects else "Umum / Lainnya"


# ==============================================================================
# 5. FUNGSI DRIVER & SCRAPING FACEBOOK (SELENIUM)
# ==============================================================================
def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Inisialisasi Selenium Chrome WebDriver dengan opsi anti-deteksi dan stabilitas."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--window-size=1280,1024")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)


def dismiss_facebook_login_popup(driver: webdriver.Chrome) -> None:
    """Menutup dialog popup login dari Facebook jika muncul agar tidak menghalangi DOM."""
    try:
        dialogs = driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')
        if len(dialogs) > 1:
            login_dialog = dialogs[1]
            close_btns = login_dialog.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close"], div[aria-label="Tutup"]')
            if close_btns:
                driver.execute_script("arguments[0].click();", close_btns[0])
                time.sleep(1.5)
    except Exception:
        pass


def expand_comments_and_scroll(driver: webdriver.Chrome, max_rounds: int = 25, target_limit: int = 300) -> None:
    """Melakukan auto-click tombol 'Lihat komentar lainnya' / replies dan auto-scroll."""
    print(f"  -> Memulai auto-scroll & expand komentar (Target: ~{target_limit} komentar)...")
    last_comment_count = 0
    stagnant_count = 0

    for rnd in range(1, max_rounds + 1):
        dismiss_facebook_login_popup(driver)
        dialogs = driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')
        container = dialogs[0] if dialogs else driver.find_element(By.TAG_NAME, "body")

        try:
            expand_xpath = (
                ".//span[contains(text(), 'View') or contains(text(), 'Lihat') or "
                "contains(text(), 'more') or contains(text(), 'sebelumnya') or "
                "contains(text(), 'lainnya') or contains(text(), 'reply') or "
                "contains(text(), 'replies') or contains(text(), 'balasan')]"
            )
            buttons = container.find_elements(By.XPATH, expand_xpath)
            for btn in buttons[:8]:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.4)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            driver.execute_script("""
                var container = arguments[0];
                container.scrollTop = container.scrollHeight;
                var allScrollables = container.querySelectorAll('*');
                for (var i = 0; i < allScrollables.length; i++) {
                    if (allScrollables[i].scrollHeight > allScrollables[i].clientHeight) {
                        allScrollables[i].scrollTop = allScrollables[i].scrollHeight;
                    }
                }
            """, container)
        except Exception:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(2.0)
        articles = container.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
        current_count = sum(
            1 for a in articles 
            if a.get_attribute("aria-label") and (
                a.get_attribute("aria-label").startswith("Comment by") or 
                a.get_attribute("aria-label").startswith("Komentar oleh")
            )
        )
        print(f"     [Putaran {rnd:02d}/{max_rounds:02d}] Komentar termuat di DOM: {current_count}")

        if current_count >= target_limit:
            print(f"  -> Target {target_limit} komentar telah tercapai!")
            break
        if current_count == last_comment_count:
            stagnant_count += 1
            if stagnant_count >= 5:
                print("  -> Penambahan komentar selesai.")
                break
        else:
            stagnant_count = 0
            last_comment_count = current_count


def parse_comments_from_html(html_source: str, post_url: str) -> List[Dict[str, Any]]:
    """Mengekstrak data komentar terstruktur (Author, Teks, Waktu, Like) dari HTML Facebook."""
    soup = BeautifulSoup(html_source, "html.parser")
    articles = soup.find_all("div", attrs={"role": "article"})
    records = []
    seen_comments = set()

    for art in articles:
        label = art.get("aria-label") or ""
        if not (label.startswith("Comment by") or label.startswith("Komentar oleh")):
            continue

        author = "Anonymous"
        published_time = ""
        m = re.match(r"(?:Comment by|Komentar oleh)\s+(.*?)(?:\s+(\d+.*(?:ago|lalu)|\d+[wmhdys]|just now|baru saja))?$", label, re.I)
        if m:
            author = m.group(1).strip()
            published_time = m.group(2).strip() if m.group(2) else ""

        like_count = 0
        rx_elem = art.find(attrs={"aria-label": re.compile(r"reactions?|tanggapan|like|suka", re.I)})
        if rx_elem:
            rx_label = rx_elem.get("aria-label", "")
            rx_match = re.search(r"([\d.,]+[KMB]?)", rx_label)
            if rx_match:
                like_count = parse_like_count(rx_match.group(1))

        dir_autos = art.find_all(attrs={"dir": "auto"})
        comment_candidates = []
        for d in dir_autos:
            txt = d.get_text().strip()
            if (
                txt
                and txt != author
                and txt not in comment_candidates
                and txt.lower() not in ["like", "reply", "balas", "suka", "bagikan", "share", "lihat balasan"]
                and not re.match(r"^\d+[wmhdys]$", txt)
            ):
                comment_candidates.append(txt)

        raw_comment = comment_candidates[0] if comment_candidates else ""
        dedup_key = (author, raw_comment)
        if raw_comment and dedup_key not in seen_comments:
            seen_comments.add(dedup_key)
            records.append({
                "post_url": post_url,
                "author": author,
                "raw_comment": raw_comment,
                "like_count": like_count,
                "published_time": published_time
            })

    return records


def scrape_facebook_comments(
    post_urls: List[str],
    limit_per_post: int = 300,
    max_scroll_rounds: int = 25,
    headless: bool = True
) -> List[Dict[str, Any]]:
    """Fungsi orkestrasi scraping komentar dari daftar URL postingan Facebook."""
    all_records: List[Dict[str, Any]] = []

    print("=" * 70)
    print("MEMULAI PROSES SCRAPING KOMENTAR FACEBOOK (SELENIUM)")
    print(f"Total Postingan Target : {len(post_urls)}")
    print(f"Batas per Postingan    : {limit_per_post} komentar")
    print(f"Mode Tampilan Browser  : {'Headless (Latar Belakang)' if headless else 'Visible (Buka Browser)'}")
    print("=" * 70)

    driver = create_driver(headless=headless)
    try:
        for idx, target_url in enumerate(post_urls, start=1):
            print(f"\n[{idx}/{len(post_urls)}] Membuka URL Postingan: {target_url}")
            driver.get(target_url)
            time.sleep(5)
            dismiss_facebook_login_popup(driver)
            expand_comments_and_scroll(driver, max_rounds=max_scroll_rounds, target_limit=limit_per_post)
            html_content = driver.page_source
            records = parse_comments_from_html(html_content, target_url)
            print(f"  -> Berhasil mengekstrak {len(records)} komentar unik dari postingan ini.")
            all_records.extend(records)
    finally:
        driver.quit()

    return all_records


# ==============================================================================
# 6. PIPELINE UTAMA (SCRAPING -> CLEANING -> SENTIMENT -> ASPECT -> EXPORT CSV)
# ==============================================================================
def run_pipeline():
    # 1. Ekstraksi Data Komentar Mentah
    raw_data = scrape_facebook_comments(
        post_urls=POST_URLS,
        limit_per_post=COMMENT_LIMIT_PER_POST,
        max_scroll_rounds=MAX_SCROLL_ROUNDS,
        headless=HEADLESS_MODE
    )

    total_raw = len(raw_data)
    if total_raw == 0:
        print("\n[PERINGATAN] Tidak ada komentar yang berhasil diambil. Periksa koneksi atau struktur link.")
        return

    # 2. Konversi ke DataFrame Pandas
    df = pd.DataFrame(raw_data)

    # 3. Data Cleaning & Sanitasi Teks Berbasis Regex
    print("\nMelakukan pembersihan data teks komentar (Regex Sanitization)...")
    df["cleaned_comment"] = df["raw_comment"].apply(clean_comment_text)

    # 4. Filter baris kosong atau komentar tanpa teks bermakna
    valid_mask = df["cleaned_comment"].apply(is_meaningful_comment)
    df_cleaned = df[valid_mask].copy()
    total_cleaned = len(df_cleaned)

    # 5. Analisis Sentimen 3 Kelas (Positif, Negatif, Netral)
    print("Melakukan analisis sentimen (Positif, Negatif, Netral)...")
    sentiment_results = df_cleaned["cleaned_comment"].apply(analyze_sentiment)
    df_cleaned["sentiment_label"] = [res[0] for res in sentiment_results]
    df_cleaned["sentiment_score"] = [res[1] for res in sentiment_results]

    # 6. Kategorisasi Aspek (Aspect-Based Rule Hint)
    print("Melakukan kategorisasi aspek isu publik...")
    df_cleaned["aspect"] = df_cleaned["cleaned_comment"].apply(classify_aspect)

    # Susun kolom sesuai urutan standar analisis
    ordered_columns = [
        "post_url",
        "author",
        "raw_comment",
        "cleaned_comment",
        "sentiment_label",
        "sentiment_score",
        "aspect",
        "like_count",
        "published_time"
    ]
    df_final = df_cleaned[ordered_columns]

    # 7. Ekspor ke format CSV dengan UTF-8 with BOM ('utf-8-sig')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_FILENAME)
    df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n[SUKSES] Dataset berhasil disimpan di: {output_path}")

    # ==============================================================================
    # 7. RINGKASAN EKSEKUSI & STATISTIK DATASET
    # ==============================================================================
    print("\n" + "=" * 70)
    print("RINGKASAN EKSEKUSI DATA SCRAPING & ANALISIS SENTIMEN (FACEBOOK)")
    print("=" * 70)
    print(f"1. Total Komentar Mentah Ditarik : {total_raw:,} baris")
    print(f"2. Total Setelah Pembersihan     : {total_cleaned:,} baris")
    print(f"3. Data Dibuang (Kosong/Simbol)  : {total_raw - total_cleaned:,} baris")

    # Sebaran Sentimen
    print("\n4. Sebaran Sentimen Komentar:")
    sentiment_counts = df_final["sentiment_label"].value_counts()
    for label, count in sentiment_counts.items():
        percentage = (count / total_cleaned) * 100
        print(f"   - {label:<10}: {count:>5} komentar ({percentage:.1f}%)")

    # Sebaran Aspek
    print("\n5. Sebaran Jumlah Komentar per Aspek:")
    exploded_aspects = (
        df_final["aspect"]
        .str.split(r" \| ")
        .explode()
        .value_counts()
    )
    for aspect_name, count in exploded_aspects.items():
        percentage = (count / total_cleaned) * 100
        print(f"   - {aspect_name:<35}: {count:>5} ({percentage:.1f}%)")

    print("\n6. Contoh Komentar per Kategori Sentimen:")
    for sent in ["Positif", "Negatif", "Netral"]:
        print(f"\n--- [Kategori: {sent.upper()}] ---")
        sub_df = df_final[df_final["sentiment_label"] == sent][["author", "cleaned_comment", "sentiment_score"]].head(2)
        print(sub_df.to_string(index=False))

    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
