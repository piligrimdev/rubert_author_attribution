import { apiClient } from "./client";
import type {
  SearchNearestRequest,
  AttributeRequest,
  NearestTextsResponse,
  VotesResponse,
  NearestTextItem,
} from "@/types/prediction";

function hasEmbeddingDistance(
  item: NearestTextItem,
): item is NearestTextItem & { distance: number } {
  return item.distance !== null && item.distance !== undefined;
}

/** Убирает фрагменты без эмбеддинга (distance == null), чтобы UI не падал на toFixed и т.п. */
function itemsWithEmbeddingOnly(
  items: NearestTextItem[],
): Array<NearestTextItem & { distance: number }> {
  return items.filter(hasEmbeddingDistance);
}

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
  return { items: itemsWithEmbeddingOnly(res.data.items) };
}

export async function attributePredict(data: AttributeRequest): Promise<VotesResponse> {
  const res = await apiClient.post<VotesResponse>("/attribute", buildBody(data));
  const items = itemsWithEmbeddingOnly(res.data.items);
  return { ...res.data, items };
}
