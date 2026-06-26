import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import type { AxiosError } from "axios";
import { strings } from "@/i18n/strings";

interface Props {
  error: AxiosError;
}

export default function PredictionError({ error }: Props) {
  const message =
    error.response?.status === 422
      ? strings.attribution.requestValidationError
      : error.message || strings.attribution.unknownError;

  return (
    <Alert severity="error" sx={{ mt: 3 }}>
      <AlertTitle>{strings.common.error}</AlertTitle>
      {message}
    </Alert>
  );
}
