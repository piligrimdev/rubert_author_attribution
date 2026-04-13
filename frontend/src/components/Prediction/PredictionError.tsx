import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import type { AxiosError } from "axios";

interface Props {
  error: AxiosError;
}

export default function PredictionError({ error }: Props) {
  const message =
    error.response?.status === 422
      ? "Сервер не смог обработать запрос. Проверьте введённый текст."
      : error.message || "Произошла неизвестная ошибка";

  return (
    <Alert severity="error" sx={{ mt: 3 }}>
      <AlertTitle>Ошибка</AlertTitle>
      {message}
    </Alert>
  );
}
