export interface Author {
  id: string;
  name: string;
  surname: string;
  last_name: string;
  provided_by: string | null;
}

export interface CreateAuthorRequest {
  name: string;
  surname: string;
  last_name: string;
}
