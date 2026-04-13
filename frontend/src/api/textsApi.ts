import { apiClient } from "./client";
import type { TextItem, CreateTextRequest } from "@/types/text";

export async function fetchTexts(): Promise<TextItem[]> {
  const res = await apiClient.get<TextItem[]>("/texts");
  return res.data;
}

export async function fetchTextsByAuthor(authorId: string): Promise<TextItem[]> {
  const res = await apiClient.get<TextItem[]>(`/texts/by_author/${authorId}`);
  return res.data;
}

export async function addText(data: CreateTextRequest): Promise<TextItem> {
  const res = await apiClient.post<TextItem>("/texts/add", data);
  return res.data;
}
