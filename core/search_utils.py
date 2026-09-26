"""Yozuvda 1-2 ta harf xato bo'lsa ham mijozni topib beradigan
oddiy "fuzzy" qidiruv yordamchisi (tashqi kutubxonasiz, faqat Python)."""


def levenshtein(a, b):
    """Ikki so'z orasidagi farq (nechta harf o'zgartirilishi kerak)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr_row = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr_row[j] = min(
                prev_row[j] + 1,      # o'chirish
                curr_row[j - 1] + 1,  # qo'shish
                prev_row[j - 1] + cost,  # almashtirish
            )
        prev_row = curr_row
    return prev_row[-1]


def max_allowed_distance(query):
    """Qidiruv so'zi qisqa bo'lsa 1 ta, uzunroq bo'lsa 2 tagacha xatoga yo'l qo'yamiz."""
    length = len(query)
    if length <= 3:
        return 1
    return 2


def fuzzy_contains(query, text):
    """`text` ichida `query`ga juda yaqin (1-2 harf farqli) bo'lak bormi?"""
    if not query:
        return True
    if not text:
        return False

    query = query.lower().strip()
    text = text.lower().strip()

    if query in text:
        return True

    max_dist = max_allowed_distance(query)

    # Butun matn bilan solishtiramiz (masalan telefon raqami yoki qisqa ism uchun)
    if abs(len(text) - len(query)) <= max_dist and levenshtein(query, text) <= max_dist:
        return True

    # Har bir so'z (ism, familiya) bilan alohida solishtiramiz
    for word in text.split():
        if abs(len(word) - len(query)) > max_dist:
            continue
        if levenshtein(query, word) <= max_dist:
            return True

    # Matnning boshidan query uzunligidagi bo'laklarini ham tekshiramiz
    # (masalan "Azizbek" ichidan "Azizb" ga yaqin narsa qidirilsa)
    step = max(1, len(query) - max_dist)
    for start in range(0, max(1, len(text) - len(query) + max_dist + 1), step):
        chunk = text[start:start + len(query)]
        if chunk and levenshtein(query, chunk) <= max_dist:
            return True

    return False
