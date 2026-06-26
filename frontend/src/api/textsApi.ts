import { apiClient } from "./client";
import type { TextItem, CreateTextRequest, EditTextRequest, EditTextResponse } from "@/types/text";

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

export async function deleteText(textId: string): Promise<void> {
  await apiClient.delete(`/texts/${textId}`);
}

export async function editText(
  textId: string,
  data: EditTextRequest,
): Promise<EditTextResponse> {
  const res = await apiClient.patch<EditTextResponse>(`/texts/${textId}`, data);
  return res.data;
}
