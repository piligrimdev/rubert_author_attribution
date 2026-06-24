import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTexts, fetchTextsByAuthor, addText, deleteText, editText } from "@/api/textsApi";
import type { TextItem, CreateTextRequest, EditTextRequest, EditTextResponse } from "@/types/text";
import type { AxiosError } from "axios";

const TEXTS_KEY = ["texts"] as const;

export function useTexts() {
  return useQuery<TextItem[], AxiosError>({
    queryKey: TEXTS_KEY,
    queryFn: fetchTexts,
  });
}

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
      qc.invalidateQueries({ queryKey: TEXTS_KEY });
      qc.invalidateQueries({ queryKey: ["texts", "by_author", variables.author_id] });
    },
  });
}

export function useDeleteText() {
  const qc = useQueryClient();
  return useMutation<void, AxiosError, { textId: string; authorId: string }>({
    mutationFn: ({ textId }) => deleteText(textId),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: TEXTS_KEY });
      qc.invalidateQueries({ queryKey: ["texts", "by_author", variables.authorId] });
    },
  });
}

export function useEditText() {
  const qc = useQueryClient();
  return useMutation<
    EditTextResponse,
    AxiosError,
    { textId: string; authorId: string; data: EditTextRequest }
  >({
    mutationFn: ({ textId, data }) => editText(textId, data),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: TEXTS_KEY });
      qc.invalidateQueries({ queryKey: ["texts", "by_author", variables.authorId] });
    },
  });
}
