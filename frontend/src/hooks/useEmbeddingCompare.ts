import { useMutation } from "@tanstack/react-query";
import {
  computeEmbeddingCompare,
  type EmbeddingCompareRequest,
} from "@/api/embeddingCompareApi";
import type { EmbeddingUmapResponse } from "@/types/embeddingUmap";
import type { AxiosError } from "axios";

export function useEmbeddingCompare() {
  return useMutation<EmbeddingUmapResponse, AxiosError, EmbeddingCompareRequest>({
    mutationFn: computeEmbeddingCompare,
  });
}
