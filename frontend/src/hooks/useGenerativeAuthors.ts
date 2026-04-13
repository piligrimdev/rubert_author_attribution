import { useQuery } from "@tanstack/react-query";
import { fetchGenerativeAuthors } from "@/api/authorsApi";
import type { Author } from "@/types/author";
import type { AxiosError } from "axios";

const GENERATIVE_AUTHORS_KEY = ["authors", "generative_enabled"] as const;

export function useGenerativeAuthors() {
  return useQuery<Author[], AxiosError>({
    queryKey: GENERATIVE_AUTHORS_KEY,
    queryFn: fetchGenerativeAuthors,
  });
}
