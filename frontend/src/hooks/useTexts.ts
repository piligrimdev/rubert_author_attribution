import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTextsByAuthor, addText } from "@/api/textsApi";
import type { TextItem, CreateTextRequest } from "@/types/text";
import type { AxiosError } from "axios";

export function useTextsByAuthor(authorId: string | undefined) {
  return useQuery<TextItem[], AxiosError>({
    queryKey: ["texts", "by_author", authorId],
    queryFn: () => fetchTextsByAuthor(authorId!),
    enabled: !!authorId,
  });
}

export function useAddText() {
  const qc = useQueryClient();
  return useMutation<TextItem, AxiosError, CreateTextRequest>({
    mutationFn: addText,
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["texts", "by_author", variables.author_id] });
    },
  });
}
