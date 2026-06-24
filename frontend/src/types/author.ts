export interface Author {
  id: string;
  name: string;
  surname: string;
  last_name: string;
  provided_by: string | null;
  /** Описание автора из API, если задано */
  description?: string | null;
}

export interface CreateAuthorRequest {
  name: string;
  surname: string;
  last_name: string;
}

export interface EditAuthorRequest {
  name?: string;
  surname?: string;
  last_name?: string;
  description?: string | null;
}

export interface EditAuthorResponse {
  id: string;
  name?: string;
  surname?: string;
  last_name?: string;
  description?: string | null;
}
