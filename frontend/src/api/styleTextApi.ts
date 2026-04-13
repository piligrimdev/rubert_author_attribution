import { apiClient } from "./client";
import type { StyleTextRequest, StyleTextResponse } from "@/types/styleText";

export async function styleText(
  data: StyleTextRequest,
): Promise<StyleTextResponse> {
  const res = await apiClient.post<StyleTextResponse>(
    "/generative/style_text",
    data,
  );
  return res.data;
}
