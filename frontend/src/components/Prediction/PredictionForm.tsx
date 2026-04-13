import { useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import SendIcon from "@mui/icons-material/Send";
import type { PredictRequest } from "@/types/prediction";

interface PredictionFormProps {
  onSubmit: (data: PredictRequest) => void;
  isLoading: boolean;
}

export default function PredictionForm({
  onSubmit,
  isLoading,
}: PredictionFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PredictRequest>({ defaultValues: { k: 5 } });

  return (
    <Paper sx={{ p: 3 }}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          <TextField
            {...register("text", {
              required: "Введите текст для анализа",
              minLength: {
                value: 50,
                message: "Текст должен содержать не менее 50 символов",
              },
            })}
            label="Текст для атрибуции"
            placeholder="Вставьте текст, авторство которого необходимо определить..."
            multiline
            minRows={5}
            maxRows={14}
            fullWidth
            error={!!errors.text}
            helperText={errors.text?.message}
          />
          <TextField
            {...register("k", {
              valueAsNumber: true,
              min: { value: 1, message: "Минимум 1" },
              max: { value: 20, message: "Максимум 20" },
            })}
            label="Количество ближайших текстов"
            type="number"
            sx={{ maxWidth: 280 }}
            error={!!errors.k}
            helperText={errors.k?.message}
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            loading={isLoading}
            endIcon={<SendIcon />}
            sx={{ alignSelf: "flex-start" }}
          >
            Определить автора
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
