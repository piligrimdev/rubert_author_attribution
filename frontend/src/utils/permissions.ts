import type { Author } from "@/types/author";
import type { TextItem } from "@/types/text";
import type { CurrentUser } from "@/types/auth";

export function isAdminUser(user: CurrentUser | undefined): boolean {
  return user?.role === "admin";
}

export function canDeleteAuthor(
  author: Author,
  user: CurrentUser | undefined,
): boolean {
  if (!user) return false;
  if (isAdminUser(user)) return true;
  return author.provided_by === user.user_id;
}

export function canDeleteText(
  text: TextItem,
  user: CurrentUser | undefined,
): boolean {
  if (!user) return false;
  if (isAdminUser(user)) return true;
  return text.provided_by === user.user_id;
}

export function canEditAuthor(
  author: Author,
  user: CurrentUser | undefined,
): boolean {
  return canDeleteAuthor(author, user);
}

export function canEditText(
  text: TextItem,
  user: CurrentUser | undefined,
): boolean {
  return canDeleteText(text, user);
}
