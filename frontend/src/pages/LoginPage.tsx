import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import LoginIcon from "@mui/icons-material/Login";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import { useAuth } from "@/context/AuthContext";
import type { LoginRequest } from "@/types/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>();

  const onSubmit = async (data: LoginRequest) => {
    setError(null);
    setLoading(true);
    try {
      await login(data);
      navigate("/");
    } catch (err: any) {
      setError(
        err.response?.status === 401
          ? "Неверный логин или пароль"
          : err.response?.data?.detail || "Ошибка авторизации",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
      }}
    >
      <Stack alignItems="center" spacing={1} sx={{ mb: 3 }}>
        <AutoStoriesIcon sx={{ fontSize: 48, color: "primary.main" }} />
        <Typography
          variant="h4"
          sx={{ fontFamily: "'Playfair Display', serif" }}
        >
          Атрибуция текста
        </Typography>
      </Stack>

      <Paper sx={{ p: 4, width: "100%", maxWidth: 420 }}>
        <Typography variant="h5" gutterBottom textAlign="center">
          Вход
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Stack spacing={2}>
            <TextField
              {...register("username", { required: "Введите логин" })}
              label="Логин"
              fullWidth
              autoFocus
              error={!!errors.username}
              helperText={errors.username?.message}
            />
            <TextField
              {...register("password", { required: "Введите пароль" })}
              label="Пароль"
              type="password"
              fullWidth
              error={!!errors.password}
              helperText={errors.password?.message}
            />
            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              loading={loading}
              startIcon={<LoginIcon />}
            >
              Войти
            </Button>
          </Stack>
        </form>

        <Typography
          variant="body2"
          textAlign="center"
          sx={{ mt: 2, color: "text.secondary" }}
        >
          Нет аккаунта?{" "}
          <Typography
            component={Link}
            to="/register"
            variant="body2"
            sx={{ color: "primary.main", textDecoration: "none" }}
          >
            Зарегистрироваться
          </Typography>
        </Typography>
      </Paper>
    </Box>
  );
}
