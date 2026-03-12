# 🚂 RAILWAY GA ULASH — TO'LIQ QO'LLANMA

## 📁 KERAKLI FAYLLAR (hammasi bir papkada bo'lsin)

```
matquizchibot/
├── MatQuizchibot_pg.py     ← asosiy bot (PostgreSQL versiyasi)
├── pg_adapter.py           ← SQLite→PostgreSQL adapter
├── requirements.txt        ← kutubxonalar ro'yxati
├── Procfile               ← Railway ishga tushirish buyrug'i
├── railway.toml           ← Railway sozlamalari
└── .gitignore             ← git dan chiqarilgan fayllar
```

---

## 1️⃣ GITHUB TAYYORLASH

### GitHub account yo'q bo'lsa:
1. **github.com** ga kiring → Sign up
2. Email bilan ro'yxatdan o'ting

### Repository yaratish:
1. GitHub da **"New repository"** bosing
2. Nom: `matquizchibot`
3. **Private** tanlang (bot token uchun)
4. **Create repository** bosing

### Fayllarni yuklash:
1. **"uploading an existing file"** linkini bosing
2. Yuqoridagi 6 ta faylni suring (drag & drop)
3. **"Commit changes"** bosing

---

## 2️⃣ RAILWAY SOZLASH

### Ro'yxatdan o'tish:
1. **railway.app** ga kiring
2. **"Login with GitHub"** bosing
3. Tasdiqlang

### Yangi loyiha:
1. **"New Project"** bosing
2. **"Deploy from GitHub repo"** tanlang
3. `matquizchibot` repositoryni tanlang
4. **"Deploy Now"** bosing

---

## 3️⃣ POSTGRESQL QO'SHISH (ENG MUHIM!)

1. Loyihangiz ichida **"+ New"** bosing
2. **"Database"** → **"PostgreSQL"** tanlang
3. Railway avtomatik `DATABASE_URL` yaratadi ✅

---

## 4️⃣ ENVIRONMENT VARIABLES (Muhim sozlamalar)

Railway dashboard → Sizning bot service → **"Variables"** tab:

| Kalit | Qiymat |
|-------|--------|
| `BOT_TOKEN` | `8310548897:AAG4...` (botingiz tokeni) |
| `DATABASE_URL` | Avtomatik to'ldiriladi (PostgreSQL qo'shganda) |

### BOT_TOKEN qo'shish:
1. **"+ New Variable"** bosing
2. Name: `BOT_TOKEN`
3. Value: BotFather dan olgan tokeningiz
4. **"Add"** bosing

---

## 5️⃣ BOT KODINI O'ZGARTIRISH

`MatQuizchibot_pg.py` faylida bu qatorni toping (taxminan 11-qator):

```python
BOT_TOKEN = "8310548897:AAG4khPevfikVGZdIo-p4ZMPF7vZq-r4eXM"
```

Uni shu ko'rinishga o'zgartiring:

```python
import os
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8310548897:AAG4khPevfikVGZdIo-p4ZMPF7vZq-r4eXM')
```

Shu qatorni ham toping:
```python
ADMIN_ID = 8296061905
```
O'zgartiring:
```python
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8296061905'))
```

---

## 6️⃣ DEPLOY QO'LLASH

1. GitHub da fayllarni yangilagandan so'ng Railway **avtomatik** yangi deploy qiladi
2. Railway dashboard → **"Deployments"** tab → loglarni kuring
3. `✅ Ma'lumotlar bazasi tayyor!` va `🚀 Bot ishlayapti!` ko'rsangiz — muvaffaqiyat!

---

## ⚠️ XATOLAR VA YECHIMLAR

### `DATABASE_URL not found`
→ PostgreSQL service qo'shdingizmi? Variables tab da `DATABASE_URL` ko'rinishi kerak

### `BOT_TOKEN invalid`
→ Variables tab da `BOT_TOKEN` to'g'ri kiritilganmi?

### `ModuleNotFoundError: pg_adapter`
→ `pg_adapter.py` fayli GitHub da bormi? Tekshiring

### Bot ishlamayapti lekin xato yo'q
→ Railway → Deployments → Logs → xatoni toping

---

## 💰 NARX

Railway **bepul tarif** (Hobby):
- $5/oy kredit — ko'p loyiha uchun yetadi
- 512MB RAM
- PostgreSQL: bepul (500MB gacha)

---

## 📱 TELEFONDAN GITHUB BILAN ISHLASH

**GitHub mobile app** (Android) orqali:
1. Play Store dan "GitHub" yuklab oling
2. Fayllarni telefonda tahrirlash mumkin
3. Yoki **github.dev** (brauzerda) — to'liq editor!

---

## 🔄 YANGILANISHLAR

Botda o'zgartirish qilsangiz:
1. GitHub da faylni yangilang
2. Railway **avtomatik** qayta deploy qiladi (1-2 daqiqa)

---

## 📞 YORDAM

Muammo bo'lsa konsolda ko'rsatilgan xatoni menga yuboring!
