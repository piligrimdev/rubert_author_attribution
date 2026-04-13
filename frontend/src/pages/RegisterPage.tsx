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
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import { useAuth } from "@/context/AuthContext";
import type { RegisterRequest } from "@/types/auth";

interface FormValues extends RegisterRequest {
  confirmPassword: string;
}

export default function RegisterPage() {
  const { register: authRegister } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>();

  const onSubmit = async (data: FormValues) => {
    setError(null);
    setLoading(true);
    try {
      await authRegister({
        username: data.username,
        password: data.password,
      });
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка регистрации");
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
          Регистрация
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Stack spacing={2}>
            <TextField
              {...register("username", {
                required: "Введите логин",
                minLength: {
                  value: 3,
                  message: "Минимум 3 символа",
                },
              })}
              label="Логин"
              fullWidth
              autoFocus
              error={!!errors.username}
              helperText={errors.username?.message}
            />
            <TextField
              {...register("password", {
                required: "Введите пароль",
                minLength: {
                  value: 4,
                  message: "Минимум 4 символа",
                },
              })}
              label="Пароль"
              type="password"
              fullWidth
              error={!!errors.password}
              helperText={errors.password?.message}
            />
            <TextField
              {...register("confirmPassword", {
                required: "Подтвердите пароль",
                validate: (v) =>
                  v === watch("password") || "Пароли не совпадают",
              })}
              label="Подтвердите пароль"
              type="password"
              fullWidth
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword?.message}
            />
            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              loading={loading}
              startIcon={<PersonAddIcon />}
            >
              Зарегистрироваться
            </Button>
          </Stack>
        </form>

        <Typography
          variant="body2"
          textAlign="center"
          sx={{ mt: 2, color: "text.secondary" }}
        >
          Уже есть аккаунт?{" "}
          <Typography
            component={Link}
            to="/login"
            variant="body2"
            sx={{ color: "primary.main", textDecoration: "none" }}
          >
            Войти
          </Typography>
        </Typography>
      </Paper>
    </Box>
  );
}
