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
import { strings } from "@/i18n/strings";

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
      setError(err.response?.data?.detail || strings.auth.registerError);
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
          {strings.app.title}
        </Typography>
      </Stack>

      <Paper sx={{ p: 4, width: "100%", maxWidth: 420 }}>
        <Typography variant="h5" gutterBottom textAlign="center">
          {strings.auth.registerTitle}
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
                required: strings.auth.usernameRequired,
                minLength: {
                  value: 3,
                  message: strings.auth.usernameMinLength,
                },
              })}
              label={strings.common.login}
              fullWidth
              autoFocus
              error={!!errors.username}
              helperText={errors.username?.message}
            />
            <TextField
              {...register("password", {
                required: strings.auth.passwordRequired,
                minLength: {
                  value: 8,
                  message: strings.auth.passwordMinLength,
                },
                validate: (value) => {
                  if (!/\p{L}/u.test(value)) {
                    return strings.auth.passwordNeedsLetter;
                  }
                  if (!/\d/.test(value)) {
                    return strings.auth.passwordNeedsDigit;
                  }
                  return true;
                },
              })}
              label={strings.common.password}
              type="password"
              fullWidth
              error={!!errors.password}
              helperText={
                errors.password?.message ?? strings.auth.passwordHint
              }
            />
            <TextField
              {...register("confirmPassword", {
                required: strings.auth.confirmPasswordRequired,
                validate: (v) =>
                  v === watch("password") || strings.auth.passwordsMismatch,
              })}
              label={strings.auth.confirmPassword}
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
              {strings.auth.registerButton}
            </Button>
          </Stack>
        </form>

        <Typography
          variant="body2"
          textAlign="center"
          sx={{ mt: 2, color: "text.secondary" }}
        >
          {strings.auth.hasAccount}{" "}
          <Typography
            component={Link}
            to="/login"
            variant="body2"
            sx={{ color: "primary.main", textDecoration: "none" }}
          >
            {strings.auth.loginButton}
          </Typography>
        </Typography>
      </Paper>
    </Box>
  );
}
