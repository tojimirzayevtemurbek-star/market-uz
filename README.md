# Qarz Daftar — Do'kon qarzdorlik platformasi

Do'konlar uchun mijozlarning qarzlarini yuritish tizimi (Django).

## Imkoniyatlari

- **Ro'yxatdan o'tish / kirish** — har bir do'kon egasi o'z hisobiga ega
- **Bosh sahifa** — umumiy to'lanmagan va to'langan qarzlar summasi, qarzdorlar soni, so'nggi harakatlar
- **Qarzdorlar ro'yxati** — barcha mijozlar, ism/familiya/telefon bo'yicha qidirish, har birining joriy qarzi
- **Mijoz sahifasi** — barcha qarz yozuvlari tarixi (sana va vaqti bilan avtomatik), yangi qarz qo'shish, "to'landi" deb belgilash, yozuvni o'chirish
- Barcha hisob-kitoblar (jami qarz, to'langan summa) **avtomatik** hisoblanadi

## O'rnatish

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser  # ixtiyoriy, admin panel uchun
python manage.py runserver
```

Brauzerda oching: **http://127.0.0.1:8000/**

## Ishlatish tartibi

1. `/register/` sahifasida do'kon nomi, login va parol bilan ro'yxatdan o'ting
2. "Yangi qarz" tugmasi orqali mijozning ismi, familiyasi, telefon raqami va (xohlasangiz) birinchi qarzini kiriting — sana avtomatik yoziladi
3. Mijoz yana kelib narsa olsa — uning sahifasiga kirib "Qarz qo'shish" formasi orqali yangi yozuv qo'shiladi (avvalgi qarzlar saqlanib qoladi)
4. Mijoz qarzini to'laganda — o'sha qarz yozuvi yonidagi **"To'landi deb belgilash"** tugmasini bosing. Bosh sahifadagi umumiy summalar o'zi yangilanadi

## Ishlab chiqarishga (production) chiqarish uchun

- `qarzdaftar/settings.py` faylida `DEBUG = False` qiling
- `SECRET_KEY` ni maxfiy saqlang (environment variable orqali)
- `ALLOWED_HOSTS` ga domeningizni qo'shing
- Statik fayllar uchun `python manage.py collectstatic` ishlating
- SQLite o'rniga PostgreSQL kabi production bazasidan foydalanish tavsiya etiladi

## Texnologiyalar

Django 6.1, SQLite (standart), Tailwind CSS (CDN orqali, dizayn uchun)
