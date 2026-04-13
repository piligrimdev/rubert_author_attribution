import {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";
import { login as apiLogin, register as apiRegister } from "@/api/authApi";
import type { LoginRequest, RegisterRequest } from "@/types/auth";

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("access_token"),
  );

  const login = useCallback(async (data: LoginRequest) => {
    const res = await apiLogin(data);
    localStorage.setItem("access_token", res.access_token);
    setToken(res.access_token);
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    const res = await apiRegister(data);
    localStorage.setItem("access_token", res.access_token);
    setToken(res.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      token,
      isAuthenticated: !!token,
      login,
      register,
      logout,
    }),
    [token, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
