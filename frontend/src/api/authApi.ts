import { apiClient } from "./client";
import type {
  LoginRequest,
  RegisterRequest,
  CurrentUser,
} from "@/types/auth";

export async function login(data: LoginRequest): Promise<void> {
  await apiClient.post("/auth/login", data);
}

export async function register(data: RegisterRequest): Promise<void> {
  await apiClient.post("/auth/register", data);
}

export async function refreshToken(): Promise<void> {
  await apiClient.post("/auth/refresh");
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
}

export async function fetchMe(): Promise<CurrentUser> {
  const res = await apiClient.get<CurrentUser>("/auth/me");
  return res.data;
}
