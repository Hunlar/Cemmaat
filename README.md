# Kur'an ve Hadis Telegram Botu

Bu bot, Telegram gruplarında ve bireysel sohbetlerde Kur'an ayetleri ve hadisler paylaşır.  
Sahibi tarafından özel `/hell` komutu ile herhangi bir gruba mesaj gönderebilir.

---

## Özellikler

- `/start` — Başlangıç mesajı  
- `/help` — Komutlar hakkında bilgi  
- `/ayet` — Rastgele Kur'an ayeti ve meali  
- Her saat başı gruplara rastgele hadis gönderimi  
- Gizli `/hell <chat_id> <mesaj>` komutu (sadece sahip kullanabilir)

---

## Deploy to Heroku

Aşağıdaki butona tıklayarak Heroku'ya kolayca kurabilirsiniz:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Hunlar/Cemmaat)

---

## Ortam Değişkenleri (Config Vars)

| Anahtar      | Açıklama                          |
|--------------|----------------------------------|
| BOT_TOKEN    | Telegram bot token (BotFather’dan) |
| OWNER_IDS    | Sahibin Telegram ID'si (virgülle ayrılabilir) |

---

## Kurulum

1. Heroku butonundan deploy yapın  
2. Config Vars kısmına `BOT_TOKEN` ve `OWNER_IDS` ekleyin  
3. Worker dyno’yu etkinleştirin:
