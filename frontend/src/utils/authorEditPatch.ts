import type { Author, EditAuthorRequest } from "@/types/author";

export interface AuthorEditFormValues {
  name: string;
  surname: string;
  last_name: string;
  description: string;
}

const EDITABLE_FIELDS = ["name", "surname", "last_name", "description"] as const;

function originalFieldValue(author: Author, field: (typeof EDITABLE_FIELDS)[number]): string {
  if (field === "description") return author.description ?? "";
  return author[field] ?? "";
}

/** Собирает PATCH-тело: только изменённые поля; очистка ранее заполненного поля → "". */
export function buildAuthorEditPatch(
  author: Author,
  current: AuthorEditFormValues,
): EditAuthorRequest {
  const patch: EditAuthorRequest = {};

  for (const field of EDITABLE_FIELDS) {
    const original = originalFieldValue(author, field);
    const value = current[field] ?? "";

    if (value === original) continue;

    if (value === "" && original !== "") {
      patch[field] = "";
    } else if (value !== "") {
      patch[field] = value;
    }
  }

  return patch;
}
