import { useQuery } from "@tanstack/react-query";
import { fetchGenres } from "@/api/genresApi";
import type { Genre } from "@/types/genre";
import type { AxiosError } from "axios";

const GENRES_KEY = ["genres"] as const;

export function useGenres() {
  return useQuery<Genre[], AxiosError>({
    queryKey: GENRES_KEY,
    queryFn: fetchGenres,
    staleTime: 5 * 60 * 1000,
  });
}

export { GENRES_KEY };
