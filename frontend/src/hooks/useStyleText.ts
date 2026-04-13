import { useMutation } from "@tanstack/react-query";
import { styleText } from "@/api/styleTextApi";
import type { StyleTextRequest, StyleTextResponse } from "@/types/styleText";
import type { AxiosError } from "axios";

export function useStyleText() {
  return useMutation<StyleTextResponse, AxiosError, StyleTextRequest>({
    mutationFn: styleText,
  });
}
