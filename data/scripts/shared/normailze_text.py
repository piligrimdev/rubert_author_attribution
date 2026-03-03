import re
import unicodedata
import validators

_INVISIBLE_CHARS_RE = re.compile(
    r'[\u200B-\u200F'   # zero-width space и компания (ZWSP, ZWNJ, ZWJ, LRM, RLM)
    r'\u2028\u2029'     # line/paragraph separator
    r'\u202A-\u202E'    # bidi-управляющие
    r'\u2060-\u206F'    # word joiner и прочие
    r'\uFEFF'           # BOM / zero-width no-break space
    r'\u00AD'           # мягкий перенос (soft hyphen)
    r']'
)

# Схлопывание горизонтальных пробелов (табы, неразрывные пробелы и т.п.),
# но НЕ переводов строки — их обрабатываем отдельно, чтобы сохранить абзацы.
_HSPACE_RE = re.compile(r'[^\S\n]+')

# 3+ перевода строки → ровно 2 (сохраняем границы абзацев).
_MULTI_NEWLINE_RE = re.compile(r'\n{3,}')

# Пробелы в начале/конце каждой строки внутри текста.
_LINE_EDGES_RE = re.compile(r'[ \t]*\n[ \t]*')

re_id = re.compile(r'id\d+')

def normalize_text(text: str, socials: bool = False) -> str:
    """
    Нормализация одной строки:
      - NFC
      - удаление невидимых/управляющих символов
      - схлопывание пробелов (кроме переводов строк)
      - схлопывание лишних переводов строк (>=3 подряд → 2)
      - trim
    """
    if not isinstance(text, str) or not text:
        return ""

    if socials:
        splited = text.split()
        result = []

        for item in splited:
            if 'id' in text:
                pass

            if re_id.search(item):
                continue

            if validators.url(item):
                continue
            if validators.email(item):
                continue

            _item = item.replace('\xa0', '')
            _item = _item.replace('\\n', '')
            result.append(_item)

        text = ' '.join(result).strip()

    if not text:
        return ""

    # 1) Unicode NFC
    text = unicodedata.normalize("NFC", text)

    # 2) Невидимые символы
    text = _INVISIBLE_CHARS_RE.sub("", text)

    # 3) Чистим пробелы вокруг \n, потом схлопываем кратные \n
    text = _LINE_EDGES_RE.sub("\n", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)

    # 4) Схлопываем горизонтальные пробелы
    text = _HSPACE_RE.sub(" ", text)

    text = re.sub(r'\s+', ' ', text)  # множественные пробелы → один
    text = re.sub(r'\n{3,}', '\n\n', text)  # больше двух переносов → два

    text = re.sub(r'Глава \w+\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'ГЛАВА \w+\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'Часть \w+\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'ЧАСТЬ \w+\.?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # номера страниц

    text = re.sub(r'\[\d+\]', '', text)  # [1], [23] — ссылки на источники
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # заголовки markdown

    # Финальная проверка — убираем пустые строки в середине
    return text.strip()