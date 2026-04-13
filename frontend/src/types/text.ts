export interface TextItem {
  text_id: string;
  text: string;
  author_id: string;
  author: string;
  genre: string;
}

export interface CreateTextRequest {
  text: string;
  author_id: string;
  genre_name: string;
}
