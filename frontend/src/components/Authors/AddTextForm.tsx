import { useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import NoteAddIcon from "@mui/icons-material/NoteAdd";

interface FormValues {
  text: string;
  genre_name: string;
}

interface AddTextFormProps {
  onSubmit: (data: FormValues) => void;
  isLoading: boolean;
}

export default function AddTextForm({ onSubmit, isLoading }: AddTextFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>();

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Добавить текст
      </Typography>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          <TextField
            {...register("genre_name", { required: "Укажите жанр" })}
            label="Жанр"
            fullWidth
            error={!!errors.genre_name}
            helperText={errors.genre_name?.message}
          />
          <TextField
            {...register("text", {
              required: "Введите текст",
              minLength: {
                value: 20,
                message: "Текст должен содержать не менее 20 символов",
              },
            })}
            label="Текст произведения"
            placeholder="Вставьте текст произведения..."
            multiline
            minRows={4}
            maxRows={12}
            fullWidth
            error={!!errors.text}
            helperText={errors.text?.message}
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            loading={isLoading}
            startIcon={<NoteAddIcon />}
            sx={{ alignSelf: "flex-start" }}
          >
            Добавить текст
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
