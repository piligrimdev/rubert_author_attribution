import type { Author } from "@/types/author";
import type { TextItem } from "@/types/text";
import { formatAuthorLabel } from "@/components/StyleText/authorLabel";

export type ProvidedByFilter = "all" | "admin" | "mine";

export interface AuthorFilterOptions {
  search: string;
  genre: string;
  providedBy: ProvidedByFilter;
  genresMap: Map<string, Set<string>>;
  currentUserId: string | null;
}

export function authorMatchesQuery(author: Author, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const label = formatAuthorLabel(author).toLowerCase();
  if (label.includes(q)) return true;
  const parts = [author.name, author.surname, author.last_name]
    .filter(Boolean)
    .map((s) => s.toLowerCase());
  return parts.some((p) => p.includes(q));
}

export function buildAuthorGenresMap(texts: TextItem[]): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>();
  for (const text of texts) {
    const genre = text.genre.trim();
    if (!genre) continue;
    const genres = map.get(text.author_id) ?? new Set<string>();
    genres.add(genre);
    map.set(text.author_id, genres);
  }
  return map;
}

export function extractUniqueGenres(texts: TextItem[]): string[] {
  const genres = new Set<string>();
  for (const text of texts) {
    const genre = text.genre.trim();
    if (genre) genres.add(genre);
  }
  return [...genres].sort((a, b) => a.localeCompare(b, "ru"));
}

export function authorMatchesGenre(
  authorId: string,
  genre: string,
  genresMap: Map<string, Set<string>>,
): boolean {
  if (!genre) return true;
  return genresMap.get(authorId)?.has(genre) ?? false;
}

export function authorMatchesProvidedBy(
  author: Author,
  filter: ProvidedByFilter,
  currentUserId: string | null,
): boolean {
  if (filter === "all") return true;
  if (filter === "admin") return author.provided_by === null;
  if (!currentUserId) return false;
  return author.provided_by === currentUserId;
}

export function filterAuthors(
  authors: Author[],
  options: AuthorFilterOptions,
): Author[] {
  return authors.filter(
    (author) =>
      authorMatchesQuery(author, options.search) &&
      authorMatchesGenre(author.id, options.genre, options.genresMap) &&
      authorMatchesProvidedBy(author, options.providedBy, options.currentUserId),
  );
}
