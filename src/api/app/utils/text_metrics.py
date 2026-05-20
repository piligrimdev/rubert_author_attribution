import re
import zlib
import math
from collections import Counter
from typing import Optional, Dict, Any, List

import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy

import nltk

import razdel
import spacy
import textstat
from lexicalrichness import LexicalRichness

import structlog
logger = structlog.get_logger(__name__)

for pkg in ['punkt', 'punkt_tab']:
    nltk.download(pkg, quiet=True)

textstat.set_lang("ru")

spacy_model_name = "ru_core_news_lg"
_nlp = spacy.load(spacy_model_name, disable=["ner"])


def tokenize_sentences(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    return [s.text.strip() for s in razdel.sentenize(text) if s.text.strip()]


def tokenize_words(text: str, remove_punct: bool = True) -> List[str]:
    if not text or not text.strip():
        return []
    tokens = [t.text for t in razdel.tokenize(text)]

    if remove_punct:
        tokens = [t for t in tokens if re.search(r'[а-яёА-ЯЁa-zA-Z0-9]', t)]
    return tokens


def tokenize_words_alpha(text: str) -> List[str]:
    return [t for t in tokenize_words(text) if re.search(r'[а-яёА-ЯЁa-zA-Z]', t)]


def count_syllables_ru(word: str) -> int:
    vowels = set('аеёиоуыэюяАЕЁИОУЫЭЮЯaeiouyAEIOUY')
    return max(1, sum(1 for ch in word if ch in vowels))


def safe_div(a, b, default=0.0):
    return a / b if b > 0 else default


def lexical_metrics(text: str) -> Dict[str, Any]:
    """
    Метрики лексического богатства и разнообразия словаря.

    Возвращает словарь с ключами:
      - token_count         : общее число слов
      - type_count          : число уникальных слов
      - ttr                 : Type-Token Ratio (type_count / token_count)
      - ttr_lower           : TTR по нижнему регистру (убирает влияние капитализации)
      - msttr               : Mean Segmental TTR (окна по 100 слов)
      - herdan_c            : log(types) / log(tokens)  — Herdan's C
      - mtld                : Measure of Textual Lexical Diversity (лучший показатель)
      - hdd                 : HD-D (lexicalrichness)
      - hapax_count         : слова, встречающиеся ровно 1 раз
      - hapax_ratio         : hapax_count / token_count
      - avg_word_len_chars  : средняя длина слова в символах
      - std_word_len_chars  : стандартное отклонение длины слов
      - long_word_ratio     : доля слов длиннее 6 букв
      - avg_word_syllables  : средняя длина слова в слогах
    """
    words = tokenize_words_alpha(text)
    words_lower = [w.lower() for w in words]
    n_tokens = len(words)
    n_types = len(set(words_lower))

    result = {
        "token_count": n_tokens,
        "type_count": n_types,
    }

    if n_tokens == 0:
        return {k: 0 for k in [
            "token_count", "type_count", "ttr", "ttr_lower", "msttr",
            "herdan_c", "mtld", "hdd", "hapax_count", "hapax_ratio",
            "avg_word_len_chars", "std_word_len_chars", "long_word_ratio",
            "avg_word_syllables"
        ]}

    result["ttr"] = safe_div(n_types, n_tokens)
    result["ttr_lower"] = safe_div(len(set(words_lower)), n_tokens)

    window = 100
    if n_tokens >= window:
        segment_ttrs = []
        for start in range(0, n_tokens - window + 1, window):
            seg = words_lower[start:start + window]
            segment_ttrs.append(len(set(seg)) / window)
        result["msttr"] = float(np.mean(segment_ttrs))
    else:
        result["msttr"] = result["ttr_lower"]

    # Herdan's C = log(types) / log(tokens)
    result["herdan_c"] = safe_div(math.log(n_types + 1), math.log(n_tokens + 1))

    if n_tokens >= 50:
        try:
            lex = LexicalRichness(" ".join(words_lower))
            result["mtld"] = lex.mtld(threshold=0.72)
            result["hdd"] = lex.hdd(draws=42)
        except Exception:
            result["mtld"] = float("nan")
            result["hdd"] = float("nan")
    else:
        result["mtld"] = float("nan")
        result["hdd"] = float("nan")

    freq = Counter(words_lower)
    hapax = sum(1 for w, c in freq.items() if c == 1)
    result["hapax_count"] = hapax
    result["hapax_ratio"] = safe_div(hapax, n_tokens)

    lengths = [len(w) for w in words]
    result["avg_word_len_chars"] = float(np.mean(lengths))
    result["std_word_len_chars"] = float(np.std(lengths))
    result["long_word_ratio"] = sum(1 for l in lengths if l > 6) / n_tokens

    ru_stopwords = set(nltk.corpus.stopwords.words("russian"))
    result['num_stopwords'] =   len([w for w in str(text).lower().split() if w in ru_stopwords])

    syllables = [count_syllables_ru(w) for w in words]
    result["avg_word_syllables"] = float(np.mean(syllables))

    return result


def syntax_metrics(text: str) -> Dict[str, Any]:
    """
    Метрики на уровне предложений и синтаксиса.

    - sent_count, avg_sent_len_words, std_sent_len_words,
        max_sent_len_words, short_sent_ratio, long_sent_ratio


    - avg_tree_depth      : средняя глубина синтаксического дерева
    - avg_clauses_per_sent: среднее число клауз (финитных глаголов) на предложение
    - avg_dep_distance    : среднее расстояние между зависимыми словами (когнитивная нагрузка)
    - avg_noun_phrases    : среднее число именных групп на предложение
    """
    sentences = tokenize_sentences(text)
    n_sents = len(sentences)

    base = {"sent_count": n_sents}
    if n_sents == 0:
        return {k: 0 for k in [
            "sent_count", "avg_sent_len_words", "std_sent_len_words",
            "max_sent_len_words", "short_sent_ratio", "long_sent_ratio",
            "avg_tree_depth", "avg_clauses_per_sent",
            "avg_dep_distance", "avg_noun_phrases"
        ]}

    # Длины предложений в словах
    sent_lens = [len(tokenize_words_alpha(s)) for s in sentences]
    base["avg_sent_len_words"] = float(np.mean(sent_lens))
    base["std_sent_len_words"] = float(np.std(sent_lens))
    base["max_sent_len_words"] = int(np.max(sent_lens))
    base["short_sent_ratio"] = sum(1 for l in sent_lens if l < 5) / n_sents
    base["long_sent_ratio"] = sum(1 for l in sent_lens if l > 40) / n_sents

    _nlp.max_length = max(_nlp.max_length, len(text) + 100)

    tree_depths, clauses, dep_dists, noun_chunks_counts = [], [], [], []

    try:
        doc = _nlp(text[:100_000])

        for sent in doc.sents:
            tokens = list(sent)
            if not tokens:
                continue

            # Глубина дерева зависимостей
            def token_depth(tok):
                d = 0
                cur = tok
                while cur.head != cur and d < 50:
                    cur = cur.head
                    d += 1
                return d
            depth = max(token_depth(t) for t in tokens)
            tree_depths.append(depth)

            # Число финитных глаголов ≈ число клауз
            n_verbs = sum(1 for t in tokens if t.pos_ == "VERB")
            clauses.append(max(1, n_verbs))

            # Средняя дистанция зависимостей (Dependency Distance)
            distances = [abs(t.i - t.head.i) for t in tokens if t.dep_ != "ROOT"]
            if distances:
                dep_dists.append(np.mean(distances))

        try:
            nc_per_sent = []
            for sent in doc.sents:
                nc = sum(1 for chunk in doc.noun_chunks
                         if chunk.start >= sent.start and chunk.end <= sent.end)
                nc_per_sent.append(nc)
            base["avg_noun_phrases"] = float(np.mean(nc_per_sent)) if nc_per_sent else float("nan")
        except Exception:
            base["avg_noun_phrases"] = float("nan")

    except Exception as e:
        base.update({
            "avg_tree_depth": float("nan"),
            "avg_clauses_per_sent": float("nan"),
            "avg_dep_distance": float("nan"),
            "avg_noun_phrases": float("nan"),
        })
        return base

    base["avg_tree_depth"] = float(np.mean(tree_depths)) if tree_depths else float("nan")
    base["avg_clauses_per_sent"] = float(np.mean(clauses)) if clauses else float("nan")
    base["avg_dep_distance"] = float(np.mean(dep_dists)) if dep_dists else float("nan")

    return base


def morphology_metrics(text: str) -> Dict[str, Any]:
    """
    Метрики частей речи и морфологии.

      - pos_*_ratio         : доля токенов каждой части речи
      - noun_verb_ratio     : NOUN / VERB (высокое = номинальный/научный стиль)
      - adj_ratio           : доля прилагательных
      - adv_ratio           : доля наречий
      - pronoun_ratio       : доля местоимений (высокое = соцсети, дневники)
      - func_word_ratio     : доля служебных слов (ключевая метрика идиостиля!)
      - first_person_ratio  : доля слов от 1-го лица (я/мы/мой/наш)
      - passive_ratio       : оценочная доля пассивных конструкций
      - past_tense_ratio    : доля глаголов прошедшего времени
    """
    result = {}

    try:
        _nlp.max_length = max(_nlp.max_length, len(text) + 100)
        doc = _nlp(text[:100_000])
        tokens = [t for t in doc if not t.is_space]
        n = len(tokens)
        if n == 0:
            raise ValueError("Пустой документ")

        pos_counts = Counter(t.pos_ for t in tokens)

        for tag in ["NOUN", "VERB", "ADJ", "ADV", "PRON",
                    "DET", "ADP", "CCONJ", "SCONJ", "PART",
                    "NUM", "INTJ", "PROPN", "PUNCT"]:
            result[f"pos_{tag.lower()}_ratio"] = safe_div(pos_counts.get(tag, 0), n)

        result["noun_verb_ratio"] = safe_div(
            pos_counts.get("NOUN", 0),
            max(pos_counts.get("VERB", 1), 1)
        )

        #  союзы, предлоги, частицы, артикли
        func_tags = {"ADP", "CCONJ", "SCONJ", "DET", "PART", "AUX"}
        result["func_word_ratio"] = safe_div(
            sum(pos_counts.get(t, 0) for t in func_tags), n
        )

        # Местоимения 1-го лица
        first_person = sum(
            1 for t in tokens
            if t.pos_ == "PRON" and t.morph.get("Person") == ["1"]
        )
        result["first_person_ratio"] = safe_div(first_person, n)

        # Пассивный залог
        passive = sum(
            1 for t in tokens
            if t.pos_ == "VERB" and "Pass" in t.morph.get("Voice", [])
        )
        result["passive_ratio"] = safe_div(passive, max(pos_counts.get("VERB", 1), 1))

        # Прошедшее время
        past = sum(
            1 for t in tokens
            if t.pos_ == "VERB" and "Past" in t.morph.get("Tense", [])
        )
        result["past_tense_ratio"] = safe_div(past, max(pos_counts.get("VERB", 1), 1))

        return result

    except Exception as e:
        pass

    return {k: float("nan") for k in [
        "noun_verb_ratio", "func_word_ratio", "first_person_ratio",
        "passive_ratio", "past_tense_ratio",
        "pos_noun_ratio", "pos_verb_ratio", "pos_adj_ratio",
        "pos_adv_ratio", "pos_pron_ratio",
    ]}



def readability_metrics(text: str) -> Dict[str, Any]:
    """
    Формульные метрики читаемости.
    Требует textstat. При его отсутствии считаются ручные версии.

    - flesch_reading_ease   : 0–100, чем выше — тем проще (>60 = лёгкий)
    - flesch_kincaid_grade  : соответствующий "класс школы"
    - gunning_fog           : акцент на многосложных словах
    - smog_index            : аналог Fog, нужно минимум 30 предложений
    - coleman_liau_index    : через символы, не слоги (надёжнее для русского)
    - ari                   : Automated Readability Index
    - avg_syllables_per_word: среднее число слогов на слово
    - polysyllable_ratio    : доля слов с 3+ слогами
    """

    try:
        return {
            "flesch_reading_ease":  textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog":          textstat.gunning_fog(text),
            "smog_index":           textstat.smog_index(text),
            "coleman_liau_index":   textstat.coleman_liau_index(text),
            "ari":                  textstat.automated_readability_index(text),
            "avg_syllables_per_word": textstat.avg_syllables_per_word(text),
            "polysyllable_ratio": safe_div(
                textstat.polysyllabcount(text),
                max(textstat.lexicon_count(text), 1)
            ),
        }
    except Exception:
        pass

    # fallback
    words = tokenize_words_alpha(text)
    sentences = tokenize_sentences(text)
    n_words = len(words)
    n_sents = len(sentences)

    if n_words == 0 or n_sents == 0:
        return {k: float("nan") for k in [
            "flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog",
            "smog_index", "coleman_liau_index", "ari",
            "avg_syllables_per_word", "polysyllable_ratio"
        ]}

    syllables_per_word = [count_syllables_ru(w) for w in words]
    avg_syll = np.mean(syllables_per_word)
    n_chars = sum(len(w) for w in words)
    avg_chars = n_chars / n_words
    avg_words_per_sent = n_words / n_sents
    polysyll = sum(1 for s in syllables_per_word if s >= 3)

    # Flesch Reading Ease
    flesch = 206.835 - 1.015 * avg_words_per_sent - 84.6 * avg_syll

    # Flesch-Kincaid Grade
    fk = 0.39 * avg_words_per_sent + 11.8 * avg_syll - 15.59

    # Gunning Fog
    fog = 0.4 * (avg_words_per_sent + 100 * polysyll / n_words)

    # Coleman-Liau
    cl = 5.88 * avg_chars - 29.6 * (n_sents / n_words) - 15.8

    # ARI
    ari = 4.71 * avg_chars + 0.5 * avg_words_per_sent - 21.43

    # SMOG (нужно минимум 30 предложений)
    smog = 3 + math.sqrt(polysyll * (30 / n_sents)) if n_sents >= 30 else float("nan")

    return {
        "flesch_reading_ease":    round(flesch, 2),
        "flesch_kincaid_grade":   round(fk, 2),
        "gunning_fog":            round(fog, 2),
        "smog_index":             round(smog, 2) if not math.isnan(smog) else float("nan"),
        "coleman_liau_index":     round(cl, 2),
        "ari":                    round(ari, 2),
        "avg_syllables_per_word": round(float(avg_syll), 3),
        "polysyllable_ratio":     round(polysyll / n_words, 3),
    }


def information_metrics(text: str) -> Dict[str, Any]:
    """
    Метрики, основанные на теории информации.

    - char_entropy      : энтропия Шеннона по символам (биты)
    - word_entropy      : энтропия по словам
    - char_entropy_norm : нормированная энтропия по символам (0–1)
    - word_entropy_norm : нормированная энтропия по словам (0–1)
    - compression_ratio : размер gzip / оригинальный размер
                          (чем меньше — тем больше повторов)
    - repetition_score  : 1 - compression_ratio (чем больше — тем повторяющийся текст)
    - bigram_entropy    : энтропия по биграммам слов
    - zipf_coefficient  : наклон Zipf-распределения (отражает стиль распределения слов)
    """
    if not text or not text.strip():
        return {k: float("nan") for k in [
            "char_entropy", "word_entropy", "char_entropy_norm",
            "word_entropy_norm", "compression_ratio", "repetition_score",
            "bigram_entropy", "zipf_coefficient"
        ]}

    # ── Символьная энтропия ──
    char_counts = Counter(text)
    total_chars = len(text)
    char_probs = np.array([c / total_chars for c in char_counts.values()])
    char_ent = float(scipy_entropy(char_probs, base=2))
    char_ent_norm = char_ent / math.log2(len(char_counts)) if len(char_counts) > 1 else 0.0

    # ── Словарная энтропия ──
    words = tokenize_words_alpha(text)
    words_lower = [w.lower() for w in words]
    n_words = len(words_lower)

    if n_words < 2:
        word_ent = word_ent_norm = bigram_ent = zipf_coef = float("nan")
    else:
        word_counts = Counter(words_lower)
        word_probs = np.array([c / n_words for c in word_counts.values()])
        word_ent = float(scipy_entropy(word_probs, base=2))
        word_ent_norm = word_ent / math.log2(len(word_counts)) if len(word_counts) > 1 else 0.0

        # Биграммная энтропия
        bigrams = list(zip(words_lower[:-1], words_lower[1:]))
        bigram_counts = Counter(bigrams)
        n_bg = len(bigrams)
        bg_probs = np.array([c / n_bg for c in bigram_counts.values()])
        bigram_ent = float(scipy_entropy(bg_probs, base=2))

        # Коэффициент Zipf: наклон в log-log пространстве (rank vs frequency)
        # Богатый стиль → крутой наклон; повторяющийся → пологий
        try:
            sorted_freqs = sorted(word_counts.values(), reverse=True)
            ranks = np.arange(1, len(sorted_freqs) + 1)
            log_ranks = np.log(ranks)
            log_freqs = np.log(sorted_freqs)
            # Линейная регрессия в log-log пространстве
            coeffs = np.polyfit(log_ranks, log_freqs, 1)
            zipf_coef = float(abs(coeffs[0]))  # отрицательный → берём модуль
        except Exception:
            zipf_coef = float("nan")

    # ── Коэффициент сжатия ──
    encoded = text.encode("utf-8")
    compressed = zlib.compress(encoded, level=9)
    comp_ratio = len(compressed) / len(encoded) if len(encoded) > 0 else 1.0

    return {
        "char_entropy":       round(char_ent, 4),
        "word_entropy":       round(word_ent, 4) if not math.isnan(word_ent) else float("nan"),
        "char_entropy_norm":  round(char_ent_norm, 4),
        "word_entropy_norm":  round(word_ent_norm, 4) if not math.isnan(word_ent_norm) else float("nan"),
        "compression_ratio":  round(comp_ratio, 4),
        "repetition_score":   round(1 - comp_ratio, 4),
        "bigram_entropy":     round(bigram_ent, 4) if not math.isnan(bigram_ent) else float("nan"),
        "zipf_coefficient":   round(zipf_coef, 4) if not math.isnan(zipf_coef) else float("nan"),
    }



def punctuation_metrics(text: str) -> Dict[str, Any]:
    """
    Метрики пунктуации, форматирования и специальных символов.

    - punct_ratio              : доля символов-пунктуации
    - exclamation_ratio        : доля '!' среди предложений
    - question_ratio           : доля '?' среди предложений
    - ellipsis_ratio           : доля '...' среди предложений (незавершённость)
    - comma_per_sentence       : запятых на предложение (синтаксическая сложность)
    - semicolon_per_sentence   : точек с запятой на предложение
    - dash_per_sentence        : тире на предложение
    - parenthesis_per_sentence : скобок на предложение
    - avg_para_len_sentences   : средняя длина абзаца в предложениях
    - emoji_ratio              : доля эмодзи среди всех символов
    - hashtag_count            : число хэштегов (#word)
    - mention_count            : число упоминаний (@word) — соцсети
    - caps_ratio               : доля слов В КАПСЛОКЕ (среди слов длиннее 2 букв)
    - repeated_punct_count     : "!!" / "..." / "???" — эмоциональные повторы
    - url_count                : число URL в тексте
    """
    if not text:
        return {k: 0 for k in [
            "punct_ratio", "exclamation_ratio", "question_ratio", "ellipsis_ratio",
            "comma_per_sentence", "semicolon_per_sentence", "dash_per_sentence",
            "parenthesis_per_sentence", "avg_para_len_sentences",
            "emoji_ratio", "hashtag_count", "mention_count", "caps_ratio",
            "repeated_punct_count", "url_count"
        ]}

    n_chars = len(text)
    sentences = tokenize_sentences(text)
    n_sents = max(len(sentences), 1)
    words = tokenize_words(text, remove_punct=False)

    punct_chars = sum(1 for c in text if c in '.,;:!?…—–-()[]{}"\'"\'')
    result = {"punct_ratio": safe_div(punct_chars, n_chars)}

    result["exclamation_ratio"]  = safe_div(text.count('!'), n_sents)
    result["question_ratio"]     = safe_div(text.count('?'), n_sents)
    result["ellipsis_ratio"]     = safe_div(text.count('...') + text.count('…'), n_sents)
    result["comma_per_sentence"] = safe_div(text.count(','), n_sents)
    result["semicolon_per_sentence"] = safe_div(text.count(';'), n_sents)

    dash_count = text.count('—') + text.count('–') + text.count(' - ')
    result["dash_per_sentence"] = safe_div(dash_count, n_sents)

    paren_count = text.count('(') + text.count('[')
    result["parenthesis_per_sentence"] = safe_div(paren_count, n_sents)

    # Абзацы
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    if paragraphs:
        para_lens = [len(tokenize_sentences(p)) for p in paragraphs]
        result["avg_para_len_sentences"] = float(np.mean(para_lens))
    else:
        result["avg_para_len_sentences"] = float(n_sents)

    # Эмодзи
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F'   # Emoticons
        r'\U0001F300-\U0001F5FF'    # Misc symbols
        r'\U0001F680-\U0001F6FF'    # Transport
        r'\U0001F1E0-\U0001F1FF'    # Flags
        r'\U00002700-\U000027BF'    # Dingbats
        r'\U0001F900-\U0001F9FF'    # Supplemental
        r'\U00002600-\U000026FF]',  # Misc symbols
        re.UNICODE
    )
    emojis = emoji_pattern.findall(text)
    result["emoji_ratio"] = safe_div(len(emojis), n_chars)

    # Соцсети-специфичные признаки
    result["hashtag_count"] = len(re.findall(r'#\w+', text))
    result["mention_count"] = len(re.findall(r'@\w+', text))

    # Капслок: слова, написанные полностью заглавными (длиннее 2 символов)
    alpha_words = [w for w in tokenize_words_alpha(text) if len(w) > 2]
    caps_words = sum(1 for w in alpha_words if w.isupper())
    result["caps_ratio"] = safe_div(caps_words, max(len(alpha_words), 1))

    # Повторяющаяся пунктуация ("!!", "???", "....." и т.д.)
    repeated = re.findall(r'[!?]{2,}|\.{3,}', text)
    result["repeated_punct_count"] = len(repeated)

    # URL
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        r'|www\.\S+'
    )
    result["url_count"] = len(url_pattern.findall(text))

    return result



def compute_text_metrics(
    text: str
) -> Dict[str, Any]:

    if not isinstance(text, str):
        text = str(text) if text else ""

    result = {}
    result.update(lexical_metrics(text))
    result.update(syntax_metrics(text))
    result.update(morphology_metrics(text))
    result.update(readability_metrics(text))
    result.update(information_metrics(text))
    result.update(punctuation_metrics(text))

    return result

def _sanitize_for_json(d: Dict[str, Any]) -> Dict[str, Any]:
    """Заменяет nan/inf на None, чтобы результат был валидным JSON."""
    sanitized = {}
    for k, v in d.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            sanitized[k] = None
        else:
            sanitized[k] = v
    return sanitized


def compute_author_metrics(
    df: pd.DataFrame,
    author_name: str,
    text_col: str = "text",
    author_col: str = "author",
) -> Dict[str, Any]:

    author_df = df[df[author_col] == author_name]

    if author_df.empty:
        raise ValueError(f"Автор '{author_name}' не найден в колонке '{author_col}'")

    logger.info("text_metrics.processing.started", author_name=author_name, texts_count=len(author_df))

    all_metrics = []
    for idx, row in author_df.iterrows():
        try:
            m = compute_text_metrics(row[text_col])
            all_metrics.append(m)
        except Exception as e:
            logger.error("text_metrics.processing.error_on_text_entry", text_inx=idx, error=e)

    if not all_metrics:
        return {}

    metrics_df = pd.DataFrame(all_metrics)

    numeric_cols = metrics_df.select_dtypes(include=[np.number]).columns

    result = {"author": author_name, "text_count": len(all_metrics)}

    for col in numeric_cols:
        vals = metrics_df[col].dropna()
        if len(vals) == 0:
            continue
        result[f"{col}_mean"]   = round(float(vals.mean()), 4)
        result[f"{col}_median"] = round(float(vals.median()), 4)
        result[f"{col}_std"]    = round(float(vals.std(ddof=0)), 4)
        result[f"{col}_min"]    = round(float(vals.min()), 4)
        result[f"{col}_max"]    = round(float(vals.max()), 4)
        result[f"{col}_q25"]    = round(float(vals.quantile(0.25)), 4)
        result[f"{col}_q75"]    = round(float(vals.quantile(0.75)), 4)

    result = _sanitize_for_json(result)
    logger.info("text_metrics.processing.finished")
    return result




