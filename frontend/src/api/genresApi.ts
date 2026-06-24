import { apiClient } from "./client";
import type { Genre } from "@/types/genre";

export async function fetchGenres(): Promise<Genre[]> {
  const res = await apiClient.get<Genre[]>("/genres");
  return res.data;
}
