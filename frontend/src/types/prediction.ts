export interface PredictRequest {
  text: string;
  k?: number;
}

export interface NearestTextItem {
  text_id: string;
  text: string;
  author_id: string;
  author: string;
  distance: number;
}

export interface PredictionResponse {
  items: NearestTextItem[];
}
