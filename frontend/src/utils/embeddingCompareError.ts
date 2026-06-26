import { strings } from "@/i18n/strings";
import axios from "axios";
import { getApiErrorDetail } from "@/utils/apiError";

export function getEmbeddingCompareErrorMessage(error: unknown): string {
  const detail = getApiErrorDetail(error, strings.metrics.umap.buildError);

  if (axios.isAxiosError(error) && error.response?.status === 500) {
    return `${detail} ${strings.metrics.umap.insufficientTexts}`;
  }

  if (detail.toLowerCase().includes("failed")) {
    return `${detail} ${strings.metrics.umap.insufficientTexts}`;
  }

  return detail;
}
