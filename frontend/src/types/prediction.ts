export interface SearchNearestRequest {
  text: string;
  k?: number;
  /** Ограничить поиск ближайших текстов указанными авторами; если не передано — по всем доступным */
  author_ids?: string[];
}

export interface AttributeRequest extends SearchNearestRequest {
  threshold: number;
}

export interface NearestTextItem {
  text_id: string;
  text: string;
  author_id: string;
  author: string;
  distance: number;
}

/** Ответ POST /nearest_k */
export interface NearestTextsResponse {
  items: NearestTextItem[];
}

/** Ответ POST /attribute */
export interface VotesResponse {
  predicted: string | null;
  confidence: number;
  avg_sim: number;
  votes: Record<string, number>;
  items: NearestTextItem[];
}

export type AttributionFormMode = "nearest" | "voting";

export type AttributionSubmitPayload =
  | { mode: "nearest"; data: SearchNearestRequest }
  | { mode: "voting"; data: AttributeRequest };
