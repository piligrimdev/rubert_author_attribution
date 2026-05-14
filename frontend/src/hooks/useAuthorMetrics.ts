import { useMutation } from "@tanstack/react-query";
import { computeAuthorMetrics } from "@/api/authorsApi";
import type { AuthorMetricsResponse } from "@/types/authorMetrics";
import type { AxiosError } from "axios";

export type AuthorMetricsPair = {
  primary: AuthorMetricsResponse;
  secondary: AuthorMetricsResponse | null;
};

export type ComputeMetricsPairVars = {
  primaryId: string;
  compareId: string | null;
};

export function useComputeAuthorMetrics() {
  return useMutation<AuthorMetricsResponse, AxiosError, string>({
    mutationFn: (authorId: string) => computeAuthorMetrics(authorId),
  });
}

/** Загрузка метрик текущего автора и, при необходимости, второго для сравнения. */
export function useComputeAuthorMetricsPair() {
  return useMutation<AuthorMetricsPair, AxiosError, ComputeMetricsPairVars>({
    mutationFn: async ({ primaryId, compareId }) => {
      const primary = await computeAuthorMetrics(primaryId);
      if (!compareId || compareId === primaryId) {
        return { primary, secondary: null };
      }
      const secondary = await computeAuthorMetrics(compareId);
      return { primary, secondary };
    },
  });
}
