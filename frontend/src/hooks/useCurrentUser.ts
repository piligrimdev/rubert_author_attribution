import { useQuery } from "@tanstack/react-query";
import { fetchMe } from "@/api/authApi";
import { useAuth } from "@/context/AuthContext";
import type { CurrentUser } from "@/types/auth";
import type { AxiosError } from "axios";

const CURRENT_USER_KEY = ["auth", "me"] as const;

export function useCurrentUser() {
  const { isAuthenticated } = useAuth();

  return useQuery<CurrentUser, AxiosError>({
    queryKey: CURRENT_USER_KEY,
    queryFn: fetchMe,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });
}

export { CURRENT_USER_KEY };
