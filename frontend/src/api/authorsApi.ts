import axios from "axios";

import { strings } from "@/i18n/strings";
import { apiClient } from "./client";
import type { Author, CreateAuthorRequest, EditAuthorRequest, EditAuthorResponse } from "@/types/author";
import type {
  AuthorMetricsResponse,
  StartComputeMetricsTaskResponse,
} from "@/types/authorMetrics";
import type {
  CorpusImportTaskStatus,
  StartCorpusImportTaskResponse,
} from "@/types/corpusImport";

const METRICS_POLL_INTERVAL_MS = 500;
const METRICS_POLL_DEADLINE_MS = 120_000;

const CORPUS_IMPORT_POLL_INTERVAL_MS = 500;
const CORPUS_IMPORT_POLL_DEADLINE_MS = 600_000;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

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

export async function deleteAuthor(authorId: string): Promise<void> {
  await apiClient.delete(`/authors/${authorId}`);
}

export async function editAuthor(
  authorId: string,
  data: EditAuthorRequest,
): Promise<EditAuthorResponse> {
  const res = await apiClient.patch<EditAuthorResponse>(`/authors/${authorId}`, data);
  return res.data;
}

/** Запускает расчёт и опрашивает GET до готовности (418 — задача ещё выполняется). */
export async function computeAuthorMetrics(
  authorId: string,
): Promise<AuthorMetricsResponse> {
  const { data: started } =
    await apiClient.post<StartComputeMetricsTaskResponse>(
      "/authors/compute_metrics",
      { author_id: authorId },
    );
  const taskId =
    typeof started.task_id === "string"
      ? started.task_id
      : String(started.task_id);

  const path = `/authors/compute_metrics/${encodeURIComponent(taskId)}`;
  const deadline = Date.now() + METRICS_POLL_DEADLINE_MS;

  while (Date.now() < deadline) {
    try {
      const res = await apiClient.get<AuthorMetricsResponse>(path);
      return res.data;
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 418) {
        await delay(METRICS_POLL_INTERVAL_MS);
        continue;
      }
      throw err;
    }
  }

  throw new Error(strings.apiErrors.metricsTimeout);
}

export async function startCorpusCsvImport(
  file: File,
): Promise<StartCorpusImportTaskResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await apiClient.post<StartCorpusImportTaskResponse>(
    "/authors/import_csv",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data;
}

export async function getCorpusCsvImportStatus(
  taskId: string,
): Promise<CorpusImportTaskStatus> {
  const res = await apiClient.get<CorpusImportTaskStatus>(
    `/authors/import_csv/${encodeURIComponent(taskId)}`,
  );
  return res.data;
}

/** Загружает CSV и опрашивает статус задачи до завершения. */
export async function importCorpusCsv(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<CorpusImportTaskStatus> {
  const { task_id: taskId } = await startCorpusCsvImport(file);
  const deadline = Date.now() + CORPUS_IMPORT_POLL_DEADLINE_MS;

  while (Date.now() < deadline) {
    const status = await getCorpusCsvImportStatus(taskId);

    if (status.progress != null && onProgress) {
      onProgress(status.progress);
    }

    if (status.status === "SUCCESS") {
      onProgress?.(100);
      return status;
    }

    if (status.status === "FAILURE") {
      throw new Error(status.error ?? strings.apiErrors.importFailed);
    }

    await delay(CORPUS_IMPORT_POLL_INTERVAL_MS);
  }

  throw new Error(strings.apiErrors.importTimeout);
}
