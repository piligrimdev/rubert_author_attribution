#!/usr/bin/env python3
"""
Асинхронный парсер сайта ilibrary.ru — Интернет-библиотека Алексея Комарова.
Создаёт датасет: автор, название произведения, полный текст.
Результат сохраняется в JSON и/или CSV.

Зависимости:
    pip install aiohttp aiofiles beautifulsoup4 lxml

Использование:
    python ilibrary_parser.py                                   # парсить всё
    python ilibrary_parser.py --authors chekhov pushkin         # только указанные
    python ilibrary_parser.py --exclude tolstoy dostoevski      # все, кроме указанных
    python ilibrary_parser.py --limit 5                         # макс. 5 произведений на автора
    python ilibrary_parser.py --concurrency 10 --delay 0.5      # 10 параллельных задач
    python ilibrary_parser.py --output my_data --format json    # имя файла и формат
"""

import argparse
import asyncio
import csv
import io
import json
import logging
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

# ─────────────────────────── config ───────────────────────────

BASE_URL = "https://ilibrary.ru"
AUTHORS_URL = f"{BASE_URL}/author.html"
ENCODING = "windows-1251"

DEFAULT_DELAY = 0.3          # сек. между запросами одного воркера
DEFAULT_CONCURRENCY = 5      # параллельных HTTP-соединений
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 3
MAX_SEQUENTIAL_PAGES = 500   # предел при итеративном переборе p.N

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────── data ─────────────────────────────

@dataclass
class Work:
    author: str
    title: str
    url: str
    text: str


# ────────────────────── async HTTP layer ──────────────────────

class AsyncFetcher:
    """Асинхронный HTTP-клиент с семафором, задержкой и повторами."""

    def __init__(
        self,
        concurrency: int = DEFAULT_CONCURRENCY,
        delay: float = DEFAULT_DELAY,
    ):
        self._semaphore = asyncio.Semaphore(concurrency)
        self._delay = delay
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=12)
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        self._session = aiohttp.ClientSession(
            connector=connector,
            headers=HEADERS,
            timeout=timeout,
        )
        return self

    async def __aexit__(self, *exc):
        if self._session:
            await self._session.close()

    # ── публичный API ──

    async def get(self, url: str) -> BeautifulSoup:
        """Загрузить страницу (с семафором/задержкой/повторами).
        Бросает RuntimeError если не удалось."""
        async with self._semaphore:
            return await self._fetch(url)

    async def get_or_none(self, url: str) -> BeautifulSoup | None:
        """Загрузить страницу. Вернёт None при любой ошибке (включая 404)."""
        try:
            return await self.get(url)
        except RuntimeError:
            return None

    async def head_ok(self, url: str) -> bool:
        """Быстрая проверка доступности URL через HEAD (для probe)."""
        async with self._semaphore:
            try:
                async with self._session.head(url, allow_redirects=True) as resp:
                    await asyncio.sleep(self._delay)
                    return resp.status == 200
            except (aiohttp.ClientError, asyncio.TimeoutError):
                return False

    async def get_many_ordered(self, urls: list[str]) -> list[BeautifulSoup | None]:
        """Параллельная загрузка нескольких URL. Порядок сохранён. None при ошибке."""
        tasks = [self.get_or_none(url) for url in urls]
        return await asyncio.gather(*tasks)

    # ── внутренняя логика ──

    async def _fetch(self, url: str) -> BeautifulSoup:
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with self._session.get(url) as resp:
                    if resp.status == 404:
                        raise RuntimeError(f"404 Not Found: {url}")
                    resp.raise_for_status()
                    raw = await resp.read()
                    html = raw.decode(ENCODING, errors="replace")
                    await asyncio.sleep(self._delay)
                    return BeautifulSoup(html, "lxml")
            except RuntimeError:
                raise  # 404 — не пытаемся повторять
            except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError) as exc:
                last_exc = exc
                log.warning("  Попытка %d/%d — %s: %s", attempt, MAX_RETRIES, url, exc)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF * attempt)
        raise RuntimeError(f"Не удалось загрузить {url}: {last_exc}")


# ────────────────────── извлечение текста ─────────────────────

def extract_text_from_page(soup: BeautifulSoup) -> str:
    """Извлекает литературный текст со страницы произведения.

    На ilibrary.ru текст произведений заключён в теги <z>…</z>.
    Внутри <z> находятся абзацы в <p> и заголовки глав в <h1>–<h5>.
    """
    # Ищем все теги <z> на странице
    z_tags = soup.find_all("z")
    if not z_tags:
        return ""

    paragraphs: list[str] = []
    for z in z_tags:
        # Собираем текст из всех дочерних блоков внутри <z>
        text = z.get_text(separator=" ", strip=True)
        if text:
            paragraphs.append(text)

        # Если внутри <z> нет блочных элементов — берём текст напрямую
        if not paragraphs:
            text = z.get_text(separator="\n", strip=True)
            if text:
                paragraphs.append(text)

    return "\n\n".join(paragraphs)


# ─────────────── определение страниц произведения ─────────────

async def discover_pages_from_toc(
    fetcher: AsyncFetcher, text_id: str,
) -> list[str] | None:
    """Стратегия 1: берём список p.N из оглавления /text/<id>/index.html.
    Возвращает None если оглавление недоступно или пустое."""
    toc_url = f"{BASE_URL}/text/{text_id}/index.html"
    soup = await fetcher.get_or_none(toc_url)
    if soup is None:
        return None

    page_nums: set[int] = set()
    for a in soup.find_all("a", href=True):
        m = re.search(rf"/text/{re.escape(text_id)}/p\.(\d+)/", a["href"])
        if m:
            page_nums.add(int(m.group(1)))

    if not page_nums:
        return None

    # Сортируем и строим URL-ы
    return [
        f"{BASE_URL}/text/{text_id}/p.{n}/index.html"
        for n in sorted(page_nums)
    ]


async def discover_pages_sequential(
    fetcher: AsyncFetcher, text_id: str,
) -> list[str]:
    """Стратегия 2 (fallback): перебираем p.1, p.2, … пока страница отвечает 200.
    Используется, если оглавление не дало результатов."""
    pages: list[str] = []
    for n in range(1, MAX_SEQUENTIAL_PAGES + 1):
        url = f"{BASE_URL}/text/{text_id}/p.{n}/index.html"
        if await fetcher.head_ok(url):
            pages.append(url)
        else:
            break
    return pages


async def get_all_page_urls(fetcher: AsyncFetcher, work_url: str) -> list[str]:
    """Определяет полный список URL страниц произведения.

    1. Извлекает text_id из любого URL вида /text/<id>/…
    2. Пробует оглавление (быстро, один запрос)
    3. Если оглавление пустое — перебирает p.1, p.2, … последовательно
    """
    m = re.search(r"/text/(\d+)", work_url)
    if not m:
        return [work_url]

    text_id = m.group(1)

    # Стратегия 1: оглавление
    pages = await discover_pages_from_toc(fetcher, text_id)
    if pages:
        return pages

    # Стратегия 2: последовательный перебор
    log.debug("    TOC пуст для text/%s, перебираю p.N последовательно", text_id)
    pages = await discover_pages_sequential(fetcher, text_id)
    if pages:
        return pages

    # Крайний случай: попробуем сам URL как единственную страницу
    return [work_url]


# ──────────────────── сборка полного текста ────────────────────

async def fetch_full_text(fetcher: AsyncFetcher, work_url: str) -> str:
    """Собирает полный текст произведения: определяет страницы, загружает параллельно."""
    page_urls = await get_all_page_urls(fetcher, work_url)
    if not page_urls:
        return ""

    log.info("    → страниц: %d", len(page_urls))

    # Параллельная загрузка всех страниц (порядок сохранён)
    soups = await fetcher.get_many_ordered(page_urls)

    parts: list[str] = []
    for i, soup in enumerate(soups):
        if soup is None:
            log.warning("    Не удалось загрузить стр. %d: %s", i + 1, page_urls[i])
            continue
        page_text = extract_text_from_page(soup)
        if page_text:
            parts.append(page_text)

    return "\n\n".join(parts)


# ──────────────────── список авторов ──────────────────────────

async def get_authors(fetcher: AsyncFetcher) -> list[tuple[str, str, str]]:
    """Возвращает [(имя, slug, url), …] всех авторов."""
    soup = await fetcher.get(AUTHORS_URL)
    authors: list[tuple[str, str, str]] = []
    for a in soup.select('a[href*="/author/"]'):
        href = a.get("href", "")
        m = re.match(r"(?:https?://ilibrary\.ru)?/author/([^/]+)/index\.html", href)
        if not m:
            continue
        slug = m.group(1)
        name = a.get_text(strip=True)
        if not name:
            continue
        full_url = urljoin(BASE_URL, href)
        authors.append((name, slug, full_url))

    # Убираем дубли
    seen: set[str] = set()
    unique = []
    for item in authors:
        if item[1] not in seen:
            seen.add(item[1])
            unique.append(item)
    log.info("Найдено авторов на сайте: %d", len(unique))
    return unique


# ──────────────── список произведений автора ──────────────────

async def get_works_for_author(
    fetcher: AsyncFetcher, author_name: str, author_url: str,
) -> list[tuple[str, str]]:
    """Возвращает [(название, url), …] для автора.
    Пробует «Полный список» (l.all), затем основную страницу."""
    all_url = author_url.replace("/index.html", "/l.all/index.html")
    try:
        soup = await fetcher.get(all_url)
    except RuntimeError:
        soup = await fetcher.get(author_url)

    works: list[tuple[str, str]] = []
    for a in soup.select('a[href*="/text/"]'):
        href = a.get("href", "")
        if not re.search(r"/text/\d+", href):
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        full_url = urljoin(BASE_URL, href)
        works.append((title, full_url))

    # Дедупликация по text_id
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for title, url in works:
        tid = re.search(r"/text/(\d+)", url)
        if not tid:
            continue
        key = tid.group(1)
        if key not in seen:
            seen.add(key)
            unique.append((title, url))

    log.info("  %s — произведений: %d", author_name, len(unique))
    return unique


# ─────────────── обработка одного автора ──────────────────────

async def process_author(
    fetcher: AsyncFetcher,
    author_name: str,
    author_url: str,
    limit: int,
    progress: str,
) -> list[Work]:
    """Скачивает все произведения одного автора."""
    log.info("[%s] Автор: %s", progress, author_name)

    try:
        works_list = await get_works_for_author(fetcher, author_name, author_url)
    except RuntimeError as exc:
        log.error("  Не удалось загрузить страницу автора %s: %s", author_name, exc)
        return []

    if limit > 0:
        works_list = works_list[:limit]

    # Параллельная загрузка произведений автора
    async def _load_one(j: int, title: str, work_url: str) -> Work | None:
        log.info("  [%d/%d] %s", j, len(works_list), title)
        try:
            text = await fetch_full_text(fetcher, work_url)
        except Exception as exc:
            log.error("    Ошибка: %s — %s", title, exc)
            return None

        if text:
            log.info("    ✓ %s — %d символов", title, len(text))
            return Work(author=author_name, title=title, url=work_url, text=text)
        else:
            log.warning("    ✗ %s — текст не извлечён", title)
            return None

    tasks = [
        _load_one(j, title, url)
        for j, (title, url) in enumerate(works_list, 1)
    ]
    results = await asyncio.gather(*tasks)
    return [w for w in results if w is not None]


# ──────────────────── сохранение ──────────────────────────────

async def save_json(works: list[Work], path: Path):
    data = [asdict(w) for w in works]
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    log.info("JSON сохранён: %s (%d записей)", path, len(data))


async def save_csv(works: list[Work], path: Path):
    """Корректное сохранение CSV через модуль csv (RFC 4180)."""
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["author", "title", "url", "text"],
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()
    for w in works:
        writer.writerow(asdict(w))

    async with aiofiles.open(path, "w", encoding="utf-8", newline="") as f:
        await f.write(buf.getvalue())
    log.info("CSV сохранён: %s (%d записей)", path, len(works))


# ──────────────────── основной pipeline ───────────────────────

async def run(args: argparse.Namespace):
    async with AsyncFetcher(
        concurrency=args.concurrency,
        delay=args.delay,
    ) as fetcher:

        # 1. Список авторов
        log.info("Загружаю список авторов...")
        all_authors = await get_authors(fetcher)

        # --authors: оставить только указанных
        if args.authors:
            slugs = {s.lower() for s in args.authors}
            all_authors = [
                (n, s, u) for n, s, u in all_authors if s.lower() in slugs
            ]
            if not all_authors:
                log.error("Авторы не найдены по slug: %s", args.authors)
                fresh = await get_authors(fetcher)
                log.info("Доступные: %s", ", ".join(s for _, s, _ in fresh))
                return

        # --exclude: убрать указанных
        if args.exclude:
            exclude_slugs = {s.lower() for s in args.exclude}
            before = len(all_authors)
            all_authors = [
                (n, s, u) for n, s, u in all_authors if s.lower() not in exclude_slugs
            ]
            excluded = before - len(all_authors)
            if excluded:
                log.info("Исключено авторов: %d (%s)", excluded, ", ".join(args.exclude))

        total = len(all_authors)
        log.info("Будет обработано авторов: %d", total)

        # 2. Обрабатываем авторов
        dataset: list[Work] = []
        for i, (name, slug, url) in enumerate(all_authors, 1):
            author_works = await process_author(
                fetcher, name, url, args.limit, f"{i}/{total}",
            )
            dataset.extend(author_works)

            # Промежуточное сохранение каждые 5 авторов
            if i % 5 == 0 and dataset:
                log.info("Промежуточное сохранение (%d записей)...", len(dataset))
                await save_json(dataset, Path(f"{args.output}_partial.json"))

        # 3. Итоговое сохранение
        if not dataset:
            log.warning("Датасет пуст — нечего сохранять.")
            return

        out = Path(args.output)
        if args.format in ("json", "both"):
            await save_json(dataset, out.with_suffix(".json"))
        if args.format in ("csv", "both"):
            await save_csv(dataset, out.with_suffix(".csv"))

        log.info(
            "Готово! Авторов: %d, произведений: %d, символов: %d",
            len({w.author for w in dataset}),
            len(dataset),
            sum(len(w.text) for w in dataset),
        )


def main():
    p = argparse.ArgumentParser(
        description="Асинхронный парсер ilibrary.ru — датасет русской литературы",
    )
    p.add_argument(
        "--authors", nargs="*", default=None,
        help="Slug-и авторов для парсинга (chekhov pushkin …). Если не указано — все.",
    )
    p.add_argument(
        "--exclude", nargs="*", default=None,
        help="Slug-и авторов для ИСКЛЮЧЕНИЯ (tolstoy dostoevski …). "
             "Применяется после --authors.",
    )
    p.add_argument(
        "--limit", type=int, default=0,
        help="Макс. кол-во произведений на автора (0 = без ограничения).",
    )
    p.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=f"Параллельных HTTP-соединений (по умолчанию {DEFAULT_CONCURRENCY}).",
    )
    p.add_argument(
        "--delay", type=float, default=DEFAULT_DELAY,
        help=f"Мин. пауза между запросами одного воркера, сек (по умолчанию {DEFAULT_DELAY}).",
    )
    p.add_argument(
        "--output", type=str, default="ilibrary_dataset",
        help="Имя выходных файлов без расширения.",
    )
    p.add_argument(
        "--format", choices=["json", "csv", "both"], default="both",
        help="Формат вывода (по умолчанию both).",
    )
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()