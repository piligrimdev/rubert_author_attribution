import { apiClient } from "./client";
import type { Author, CreateAuthorRequest } from "@/types/author";
import type { AuthorMetricsResponse } from "@/types/authorMetrics";

export async function fetchAuthors(): Promise<Author[]> {
  const res = await apiClient.get<Author[]>("/authors");
  return res.data;
}

export async function fetchGenerativeAuthors(): Promise<Author[]> {
  const res = await apiClient.get<Author[]>("/authors/generative_enabled");
  return res.data;
}

export async function createAuthor(data: CreateAuthorRequest): Promise<Author> {
  const res = await apiClient.post<Author>("/authors/create", data);
  return res.data;
}

export async function computeAuthorMetrics(
  authorId: string,
): Promise<AuthorMetricsResponse> {
  const res = await apiClient.post<AuthorMetricsResponse>(
    "/authors/compute_metrics",
    { author_id: authorId },
  );
  return res.data;
}
