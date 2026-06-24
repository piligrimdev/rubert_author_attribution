import axios from "axios";
import { getApiErrorDetail } from "@/utils/apiError";

const INSUFFICIENT_TEXTS_HINT =
  "Возможно, у одного из авторов недостаточно текстов для расчёта UMAP — добавьте тексты и попробуйте позже.";

export function getEmbeddingCompareErrorMessage(error: unknown): string {
  const detail = getApiErrorDetail(error, "Не удалось построить UMAP-проекцию.");

  if (axios.isAxiosError(error) && error.response?.status === 500) {
    return `${detail} ${INSUFFICIENT_TEXTS_HINT}`;
  }

  if (detail.toLowerCase().includes("failed")) {
    return `${detail} ${INSUFFICIENT_TEXTS_HINT}`;
  }

  return detail;
}
