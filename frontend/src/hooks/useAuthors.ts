import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAuthors, createAuthor } from "@/api/authorsApi";
import type { Author, CreateAuthorRequest } from "@/types/author";
import type { AxiosError } from "axios";

const AUTHORS_KEY = ["authors"] as const;

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
