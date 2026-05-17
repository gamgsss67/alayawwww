import requests
import json
import random
import string
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import sys
import nest_asyncio

# Colab için asyncio fix (Render'da da sorun olmaz)
nest_asyncio.apply()

def random_email():
    uzunluk = random.randint(6, 10)
    rastgele_kisim = ''.join(random.choices(string.ascii_lowercase + string.digits, k=uzunluk))
    domainler = ["guerrillamail.info", "mailinator.com", "10minute.net"]
    return f"{rastgele_kisim}@{random.choice(domainler)}"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!  PROXY LİSTENİ AŞAĞIDAKİ YERE, KENDİ PROXY'LERİNLE DEĞİŞTİR   !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
PROXY_LIST = [
    "socks4://158.178.198.31:1080",
    "socks5://193.25.215.182:22222",
    "socks4://152.53.53.166:1080",
    "socks4://45.144.49.156:1080",
    "socks4://43.162.99.202:1080",
    "socks5://134.122.64.174:1080",
    "socks5://121.169.46.116:1090",
    "socks5://121.169.46.116:1090",
    "socks5://5.42.123.61:1080",
    "socks5://5.255.103.55:1080",
    "socks4://77.232.142.77:31336",
    "socks4://152.70.91.193:40000",
    "socks5://123.0.25.156:9090",
    "socks4://202.141.161.51:7891",
    "socks5://185.125.201.149:7443",
]

def proxy_dict_from_string(proxy_str):
    if '://' not in proxy_str:
        return None
    protocol = proxy_str.split('://')[0]
    addr = proxy_str.split('://')[1]
    if protocol in ['socks4', 'socks5', 'http', 'https']:
        if protocol == 'socks4':
            return {
                'http': f"socks5://{addr}",
                'https': f"socks5://{addr}"
            }
        return {
            'http': f"{protocol}://{addr}",
            'https': f"{protocol}://{addr}"
        }
    return None

def kayit_ol_sync(email, referans_kodu, proxy_str):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        'content-type': "application/json",
        'apikey': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2aWRseHV4dGFrZGlkc3p4ZXVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3MzYwNTEsImV4cCI6MjA4NzMxMjA1MX0.ffUBzkS18Yeh5njBF4qYR5xY2LIZK8KPfCTDJmFcZ_k",
        'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2aWRseHV4dGFrZGlkc3p4ZXVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3MzYwNTEsImV4cCI6MjA4NzMxMjA1MX0.ffUBzkS18Yeh5njBF4qYR5xY2LIZK8KPfCTDJmFcZ_k",
        'origin': "https://novixlibrary.com",
        'referer': "https://novixlibrary.com/",
        'accept-language': "tr",
        'Connection': 'close'
    }

    url = "https://bvidlxuxtakdidszxeuh.supabase.co/auth/v1/signup"
    params = {'redirect_to': "https://novixlibrary.com"}

    payload = {
        "email": email,
        "password": "den2333iz3deniz@deniz.con.tc",
        "data": {
            "display_name": f"User_{random.randint(1000, 9999)}",
            "referred_by": referans_kodu
        },
        "gotrue_meta_security": {},
        "code_challenge": None,
        "code_challenge_method": None
    }

    proxy_dict = proxy_dict_from_string(proxy_str)

    try:
        response = requests.post(url, params=params, json=payload,
                                headers=headers, proxies=proxy_dict, timeout=5)

        if response.status_code == 200:
            try:
                veri = response.json()
                if 'id' in veri:
                    return True, veri['id'], None
                else:
                    return False, None, "Invalid response"
            except:
                return False, None, "JSON error"
        else:
            # Hata kodunu yazdır
            print(f"API Hata Kodu: {response.status_code} - {response.text[:100]}")
            return False, None, f"HTTP {response.status_code}"

    except Exception as e:
        print(f"İstek Hatası: {str(e)[:100]}")
        return False, None, str(e)[:40]

async def kayit_ol_async(email, referans_kodu, proxy_str, executor):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, kayit_ol_sync, email, referans_kodu, proxy_str)
    return result

async def run_for_referans(referans_kodu, hedef_kayit, thread_id, proxy_queue, proxy_lock, executor):
    basarili_thread = 0
    current_proxy = None

    print(f"[Thread-{thread_id}] Basladi, hedef: {hedef_kayit} kayit - Ref: {referans_kodu}")

    for i in range(hedef_kayit):
        if current_proxy is None:
            async with proxy_lock:
                if proxy_queue:
                    current_proxy = proxy_queue.popleft()
                    print(f"[Thread-{thread_id}] Yeni proxy alindi: {current_proxy[:40]}")
                else:
                    print(f"[Thread-{thread_id}] Proxy kalmadi!")
                    break

        email = random_email()

        basarili, user_id, hata = await kayit_ol_async(email, referans_kodu, current_proxy, executor)

        if basarili:
            print(f"[Thread-{thread_id}] [{i+1}/{hedef_kayit}] {email[:20]} -> [OK] {user_id[:8]}...")
            basarili_thread += 1
        else:
            print(f"[Thread-{thread_id}] [{i+1}/{hedef_kayit}] {email[:20]} -> [X] {hata}")
            current_proxy = None # Hata alınca proxy değiştir

    print(f"[Thread-{thread_id}] Tamamlandi! Basarili: {basarili_thread}/{hedef_kayit} - Ref: {referans_kodu}")
    return basarili_thread

async def main_async(referans_kodlari, istek_sayisi, proxy_list):
    executor = ThreadPoolExecutor(max_workers=1)
    results = []

    for idx, referans_kodu in enumerate(referans_kodlari):
        start_time = time.time()

        print("\n" + "=" * 70)
        print(f"[{idx+1}/{len(referans_kodlari)}] ISLEM BASLIYOR: {referans_kodu}")
        print(f"[*] Hedef: {istek_sayisi} kayit")
        print("=" * 70)

        # Her referans kodu için proxy kuyruğunu yeniden oluştur
        proxy_queue = deque(proxy_list.copy())
        proxy_lock = asyncio.Lock()

        task = run_for_referans(referans_kodu, istek_sayisi, 1, proxy_queue, proxy_lock, executor)
        result = await task
        results.append(result)

        elapsed = time.time() - start_time
        print(f"\n[!] {referans_kodu} islemi {elapsed:.1f} saniyede tamamlandi. Basarili: {result}/{istek_sayisi}")

        # Bekleme kontrolü (son referanstan sonra bekleme)
        if idx < len(referans_kodlari) - 1:
            wait_time = 15 * 60
            if elapsed < wait_time:
                kalan_bekleme = wait_time - elapsed
                print(f"\n[!] 15 dakika bekleniyor... ({kalan_bekleme/60:.1f} dakika)")
                await asyncio.sleep(kalan_bekleme)
                print(f"[!] Bekleme bitti! Sıradaki referans koduna geçiliyor...")
            else:
                print(f"\n[!] İşlem {elapsed/60:.1f} dakika sürdü, 15 dakika dolmuş. Direkt geçiliyor.")

    executor.shutdown()
    return results

def main():
    print("=" * 70)
    print("SUPABASE OTOMATIK KAYIT ARACI - RENDER MODU")
    print("Her referans kodu için 225 kayıt + 15 dakika bekleme")
    print("=" * 70)

    # --- PROXY KONTROLÜ ---
    # Artık PROXY_LIST'i doğrudan kullanıyoruz, dosyadan okumuyoruz.
    proxy_list = PROXY_LIST
    if not proxy_list:
        print("[X] PROXY_LIST boş! Lütfen kodun içindeki PROXY_LIST değişkenini doldurun.")
        return

    print(f"[!] {len(proxy_list)} adet proxy yüklendi")

    # --- REFERANS KODLARI ---
    referans_kodlari = [
        "1E72743A", "0D35F472", "EB6CB0E2", "5FFFAE00", "A7F519D9",
        "87105E74", "D157A34B", "EA1CB196", "C4690E30", "B91697A2",
        "AC9165B4", "25B67A6B", "8A58F600", "29B91DED", "E4AD5C2A",
        "6B4617E9", "2A3ADF63", "D9CAFE06", "66D8A78E", "0E5738E0",
        "1579C933", "1130F14C", "BA782D93", "6FC58681", "81000707",
        "2E2714E9", "37FCB9CF", "66310E9E", "392B4F11", "5B4B5DA6",
        "9B0815D1", "561E1124", "5C7E2D55", "73D23F01"
    ]

    print(f"\n[!] {len(referans_kodlari)} adet referans kodu yüklendi")
    istek_sayisi = 225
    toplam_hedef = len(referans_kodlari) * istek_sayisi
    print(f"\n[!] Her referans için: {istek_sayisi} kayit")
    print(f"[!] Toplam hedef: {toplam_hedef} kayit")
    print("=" * 70)

    print("\n[!] Render'da çalışıyor... Bilgisayarını kapatabilirsin!")
    print("[!] Logları Render Dashboard'dan takip edebilirsin.")
    sys.stdout.flush()  # Çıktının hemen görünmesini sağlar

    try:
        start = time.time()
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(main_async(referans_kodlari, istek_sayisi, proxy_list))
        elapsed = time.time() - start

        print("\n" + "=" * 70)
        print("ISLEM TAMAMLANDI!")
        print(f"[OK] Toplam Basarili: {sum(results)}/{toplam_hedef}")
        print(f"[*] Basari Orani: %{(sum(results)/toplam_hedef*100):.1f}")
        print(f"[*] Gecen Sure: {elapsed/60:.1f} dakika ({elapsed/3600:.1f} saat)")

        print("\n[*] DETAYLI RAPOR:")
        for i, (ref, res) in enumerate(zip(referans_kodlari, results)):
            print(f"    {i+1}. {ref}: {res}/{istek_sayisi} basarili")
        print("=" * 70)
    except Exception as e:
        print(f"\n[X] BEKLENMEYEN HATA: {e}")
        import traceback
        traceback.print_exc() # Detaylı hata ayıklama için

if __name__ == "__main__":
    main()
