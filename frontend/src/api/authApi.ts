import { apiClient } from "./client";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
} from "@/types/auth";

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/login", data);
  return res.data;
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/register", data);
  return res.data;
}

export async function refreshToken(): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/refresh");
  return res.data;
}
