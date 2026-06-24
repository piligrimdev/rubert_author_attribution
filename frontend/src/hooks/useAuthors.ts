import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAuthors, createAuthor, deleteAuthor, editAuthor } from "@/api/authorsApi";
import type { Author, CreateAuthorRequest, EditAuthorRequest, EditAuthorResponse } from "@/types/author";
import type { AxiosError } from "axios";

const AUTHORS_KEY = ["authors"] as const;
const TEXTS_KEY = ["texts"] as const;

export function useAuthors() {
  return useQuery<Author[], AxiosError>({
    queryKey: AUTHORS_KEY,
    queryFn: fetchAuthors,
  });
}

export function useCreateAuthor() {
  const qc = useQueryClient();
  return useMutation<Author, AxiosError, CreateAuthorRequest>({
    mutationFn: createAuthor,
    onSuccess: () => qc.invalidateQueries({ queryKey: AUTHORS_KEY }),
  });
}

export function useDeleteAuthor() {
  const qc = useQueryClient();
  return useMutation<void, AxiosError, string>({
    mutationFn: deleteAuthor,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: AUTHORS_KEY });
      qc.invalidateQueries({ queryKey: TEXTS_KEY });
    },
  });
}

export function useEditAuthor() {
  const qc = useQueryClient();
  return useMutation<
    EditAuthorResponse,
    AxiosError,
    { authorId: string; data: EditAuthorRequest }
  >({
    mutationFn: ({ authorId, data }) => editAuthor(authorId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: AUTHORS_KEY }),
  });
}
