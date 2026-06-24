export interface TextItem {
  text_id: string;
  text: string;
  author_id: string;
  author: string;
  genre: string;
  provided_by: string;
}

export interface CreateTextRequest {
  text: string;
  author_id: string;
  genre_name: string;
}

export interface EditTextRequest {
  text?: string;
}

export interface EditTextResponse {
  id: string;
  text?: string;
}
