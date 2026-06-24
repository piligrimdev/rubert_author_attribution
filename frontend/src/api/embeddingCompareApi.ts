import axios from "axios";

import { apiClient } from "./client";
import type { EmbeddingUmapResponse } from "@/types/embeddingUmap";
import type { StartComputeMetricsTaskResponse } from "@/types/authorMetrics";
import { getEmbeddingCompareErrorMessage } from "@/utils/embeddingCompareError";

const POLL_INTERVAL_MS = 500;
const POLL_DEADLINE_MS = 120_000;

const TASK_FAILED_MESSAGE =
  "Задача расчёта UMAP завершилась с ошибкой. Возможно, у одного из авторов недостаточно текстов — добавьте тексты и попробуйте позже.";

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export type EmbeddingCompareRequest = {
  author_id_1: string;
  author_id_2: string;
  max_per_author?: number;
};

/** Запускает UMAP-сравнение и опрашивает GET до готовности (418 — задача ещё выполняется). */
export async function computeEmbeddingCompare(
  data: EmbeddingCompareRequest,
): Promise<EmbeddingUmapResponse> {
  const { data: started } = await apiClient.post<StartComputeMetricsTaskResponse>(
    "/texts/embedding_compare",
    data,
  );
  const taskId =
    typeof started.task_id === "string"
      ? started.task_id
      : String(started.task_id);

  const path = `/texts/embedding_compare/${encodeURIComponent(taskId)}`;
  const deadline = Date.now() + POLL_DEADLINE_MS;

  while (Date.now() < deadline) {
    try {
      const res = await apiClient.get<EmbeddingUmapResponse>(path);
      return res.data;
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 418) {
        await delay(POLL_INTERVAL_MS);
        continue;
      }
      if (axios.isAxiosError(err) && err.response?.status === 500) {
        throw new Error(getEmbeddingCompareErrorMessage(err));
      }
      throw err;
    }
  }

  throw new Error(TASK_FAILED_MESSAGE);
}
