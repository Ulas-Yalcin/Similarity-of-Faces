import os
import time
from icrawler.builtin import BingImageCrawler

# Text dosyası yolu
TXT_DOSYA = "C:/Users/yalci/Desktop/Future dreams/Similarity of Faces/celebrities.txt"

# Tüm resimlerin kaydedileceği tek klasör
KAYIT_KLASORU = r"C:\Users\yalci\Desktop\Future dreams\Similarity of Faces\pictures_of_celebrities"

# Log dosyası
LOG_DOSYA = "C:/Users/yalci/Desktop/Future dreams/Similarity of Faces/errors.log"

def log_hata(mesaj: str):
    """Hataları hem ekrana hem log dosyasına yaz."""
    print(mesaj)
    try:
        with open(LOG_DOSYA, "a", encoding="utf-8") as log:
            log.write(mesaj + "\n")
    except Exception as e:
        print(f"❌ Log dosyasına yazarken hata: {e}")

def main():
    # Klasörü oluştur
    try:
        if not os.path.exists(KAYIT_KLASORU):
            os.makedirs(KAYIT_KLASORU)
    except Exception as e:
        log_hata(f"❌ Kayıt klasörü oluşturulurken hata: {e}")
        return

    # Text dosyasını oku
    try:
        with open(TXT_DOSYA, "r", encoding="utf-8") as f:
            unlu_listesi = [satir.strip() for satir in f.readlines() if satir.strip()]
        if not unlu_listesi:
            log_hata("❌ Dosya boş veya geçerli ünlü bulunamadı.")
            return
    except FileNotFoundError:
        log_hata(f"❌ Dosya bulunamadı: {TXT_DOSYA}")
        return
    except Exception as e:
        log_hata(f"❌ Dosya okunurken hata: {e}")
        return

    # Her ünlü için fotoğraf indir
    sayac = 1
    for unlu in unlu_listesi:
        try:
            print(f"\n🔍 {unlu} için fotoğraf indiriliyor...")

            # Retry mekanizması
            basarili = False
            for deneme in range(3):
                try:
                    crawler = BingImageCrawler(storage={"root_dir": KAYIT_KLASORU})
                    crawler.crawl(
                        keyword=unlu,
                        max_num=2,  # Her ünlü için kaç fotoğraf
                        file_idx_offset=sayac-1  # Dosya isimlerini çakışmadan sıraya koymak için
                    )
                    sayac += 3  # Sonraki ünlü için sayacı artır
                    print(f"✅ {unlu} fotoğrafları indirildi. (Deneme {deneme+1})")
                    basarili = True
                    break
                except Exception as e:
                    log_hata(f"❌ {unlu} için indirme hatası (deneme {deneme+1}): {e}")
                    time.sleep(2)

            if not basarili:
                log_hata(f"❌ {unlu} için 3 denemede de indirilemedi.")

        except Exception as e:
            log_hata(f"❌ {unlu} işlenirken beklenmedik hata: {e}")
            continue

    print("\n🎉 Tüm ünlülerin fotoğrafları tek klasöre indirildi!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹ Kullanıcı tarafından durduruldu.")
    except Exception as e:
        log_hata(f"❌ Program çalışırken beklenmedik bir hata oluştu: {e}")
