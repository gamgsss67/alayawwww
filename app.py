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

# Colab için asyncio fix
nest_asyncio.apply()

def random_email():
    uzunluk = random.randint(6, 10)
    rastgele_kisim = ''.join(random.choices(string.ascii_lowercase + string.digits, k=uzunluk))
    domainler = ["guerrillamail.info", "mailinator.com", "10minute.net"]
    return f"{rastgele_kisim}@{random.choice(domainler)}"

def load_proxies():
    try:
        with open("calisanlar.txt", "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        print("[X] calisanlar.txt bulunamadi!")
        return []

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
        'apikey': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2aWRseHV4dGFrZGlkc3p4ZXVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3MzYwNTEsImV4cCI6MjA4NzMxMjA1MX0.ffUBzkS18Yeh5njBF4qYR5Yx2LIZK8KPfCTDJmFcZ_k",
        'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2aWRseHV4dGFrZGlkc3p4ZXVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3MzYwNTEsImV4cCI6MjA4NzMxMjA1MX0.ffUBzkS18Yeh5njBF4qYR5Yx2LIZK8KPfCTDJmFcZ_k",
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
            return False, None, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, None, str(e)[:40]

async def kayit_ol_async(email, referans_kodu, proxy_str, executor):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, kayit_ol_sync, email, referans_kodu, proxy_str)
    return result

async def run_for_referans(referans_kodu, hedef_kayit, thread_id, proxy_queue, proxy_lock, executor):
    """Global proxy kuyrugu kullan - her thread ayni kuyrugu paylasir"""
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
        else:
            print(f"[Thread-{thread_id}] [{i+1}/{hedef_kayit}] {email[:20]} -> [X] {hata}")
            print(f"[Thread-{thread_id}] Proxy hata verdi, yenisi aliniyor...")
            current_proxy = None
    
    print(f"[Thread-{thread_id}] Tamamlandi! Basarili: {basarili_thread}/{hedef_kayit} - Ref: {referans_kodu}")
    return basarili_thread

async def main_async(referans_kodlari, istek_sayisi, proxy_list):
    executor = ThreadPoolExecutor(max_workers=1)  # 1 thread yeterli
    
    results = []
    
    for idx, referans_kodu in enumerate(referans_kodlari):
        start_time = time.time()
        
        print("\n" + "=" * 70)
        print(f"[{idx+1}/{len(referans_kodlari)}] ISLEM BASLIYOR: {referans_kodu}")
        print(f"[*] Hedef: {istek_sayisi} kayit")
        print("=" * 70)
        
        # Her referans kodu için yeni proxy kuyruğu
        proxy_queue = deque(proxy_list.copy())
        proxy_lock = asyncio.Lock()
        
        # Sadece 1 thread ile çalış
        task = run_for_referans(referans_kodu, istek_sayisi, 1, proxy_queue, proxy_lock, executor)
        result = await task
        results.append(result)
        
        elapsed = time.time() - start_time
        print(f"\n[!] {referans_kodu} islemi {elapsed:.1f} saniyede tamamlandi. Basarili: {result}/{istek_sayisi}")
        
        # Bekleme kontrolü
        if idx < len(referans_kodlari) - 1:
            wait_time = 15 * 60  # 15 dakika
            
            if elapsed < wait_time:
                kalan_bekleme = wait_time - elapsed
                print(f"\n[!] 15 dakika bekleniyor... ({kalan_bekleme/60:.1f} dakika)")
                
                for remaining in range(int(kalan_bekleme), 0, -1):
                    if remaining % 60 == 0:
                        print(f"[*] Kalan süre: {remaining//60} dakika {remaining%60} saniye")
                    await asyncio.sleep(1)
                print(f"[!] Bekleme bitti! Sıradaki referans koduna geçiliyor...")
            else:
                print(f"\n[!] İşlem {elapsed/60:.1f} dakika sürdü, 15 dakika dolmuş. Direkt geçiliyor.")
    
    executor.shutdown()
    return results

def main():
    print("=" * 70)
    print("SUPABASE OTOMATIK KAYIT ARACI - GECE MODU")
    print("Her referans kodu için 225 kayıt + 15 dakika bekleme")
    print("=" * 70)
    
    # Proxy yükle
    proxy_list = load_proxies()
    if not proxy_list:
        print("\n[!] calisanlar.txt bulunamadi!")
        print("Önce 'calisanlar.txt' dosyasını yükleyin veya oluşturun.")
        return
    
    print(f"[!] {len(proxy_list)} adet proxy yüklendi")
    
    # Referans kodlarını al - YANYANA veya SATIR SATIR
    print("\nReferans kodlarini girin (boşluk veya enter ile ayirabilirsiniz):")
    print("Örnek: BA782D93 2982D03C 610D5EB0")
    referans_input = input("Referans kodlari: ").strip()
    
    # Boşluk ve enter ile ayır
    referans_kodlari = referans_input.split()
    
    # Eğer hiç girilmemişse veya sadece enter basılmışsa
    if len(referans_kodlari) == 0:
        print("[X] En az bir referans kodu girmelisiniz!")
        return
    
    print(f"\n[!] {len(referans_kodlari)} adet referans kodu girildi:")
    for i, ref in enumerate(referans_kodlari):
        print(f"    {i+1}. {ref}")
    
    # SABİT: Her referans kodu için 225 kayıt
    istek_sayisi = 225
    
    toplam_hedef = len(referans_kodlari) * istek_sayisi
    toplam_bekleme = (len(referans_kodlari) - 1) * 15  # dakika cinsinden
    print(f"\n[!] Her referans için: {istek_sayisi} kayit")
    print(f"[!] Toplam hedef: {toplam_hedef} kayit")
    print(f"[!] Toplam proxy: {len(proxy_list)}")
    print(f"[!] Toplam bekleme: {toplam_bekleme} dakika (referanslar arası)")
    print("=" * 70)
    
    input("\n[!] Enter'a basarak başlayın (gece boyu çalışacak)...")
    
    try:
        start = time.time()
        # Colab için doğru asyncio çağrısı
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
    except KeyboardInterrupt:
        print("\n\n[!] Ctrl+C algilandi! Program durduruldu.")
    except Exception as e:
        print(f"\n[X] Hata: {e}")

if __name__ == "__main__":
    main()