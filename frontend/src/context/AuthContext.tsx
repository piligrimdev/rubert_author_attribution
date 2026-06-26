import {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  useEffect,
  type ReactNode,
} from "react";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  fetchMe,
} from "@/api/authApi";
import type { LoginRequest, RegisterRequest } from "@/types/auth";

interface AuthState {
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    localStorage.removeItem("access_token");

    fetchMe()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false))
      .finally(() => setIsBootstrapping(false));
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    await apiLogin(data);
    setIsAuthenticated(true);
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    await apiRegister(data);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      setIsAuthenticated(false);
    }
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      isAuthenticated,
      isBootstrapping,
      login,
      register,
      logout,
    }),
    [isAuthenticated, isBootstrapping, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
