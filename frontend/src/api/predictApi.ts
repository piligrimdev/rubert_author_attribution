import { apiClient } from "./client";
import type {
  SearchNearestRequest,
  AttributeRequest,
  NearestTextsResponse,
  VotesResponse,
} from "@/types/prediction";

function buildBody<T extends SearchNearestRequest>(data: T): Record<string, unknown> {
  const { author_ids, ...rest } = data;
  return {
    ...rest,
    ...(author_ids?.length ? { author_ids } : {}),
  };
}

export async function searchNearest(
  data: SearchNearestRequest,
): Promise<NearestTextsResponse> {
  const res = await apiClient.post<NearestTextsResponse>("/nearest_k", buildBody(data));
  return res.data;
}

export async function attributePredict(data: AttributeRequest): Promise<VotesResponse> {
  const res = await apiClient.post<VotesResponse>("/attribute", buildBody(data));
  return res.data;
}
