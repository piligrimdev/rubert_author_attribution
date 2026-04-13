import { useMutation } from "@tanstack/react-query";
import { predict } from "@/api/predictApi";
import type { PredictRequest, PredictionResponse } from "@/types/prediction";
import type { AxiosError } from "axios";

export function usePrediction() {
  return useMutation<PredictionResponse, AxiosError, PredictRequest>({
    mutationFn: predict,
  });
}
