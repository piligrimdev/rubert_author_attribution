import type { Author } from "@/types/author";

export function formatAuthorLabel(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}
