import { apiClient } from "./client";
import type { PredictRequest, PredictionResponse } from "@/types/prediction";

export async function predict(data: PredictRequest): Promise<PredictionResponse> {
  const res = await apiClient.post<PredictionResponse>("/predict", data);
  return res.data;
}
