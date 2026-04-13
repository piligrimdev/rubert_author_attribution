import { useMutation } from "@tanstack/react-query";
import { computeAuthorMetrics } from "@/api/authorsApi";
import type { AuthorMetricsResponse } from "@/types/authorMetrics";
import type { AxiosError } from "axios";

export function useComputeAuthorMetrics() {
  return useMutation<AuthorMetricsResponse, AxiosError, string>({
    mutationFn: (authorId: string) => computeAuthorMetrics(authorId),
  });
}
