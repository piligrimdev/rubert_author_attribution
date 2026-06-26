import { Controller, useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import NoteAddIcon from "@mui/icons-material/NoteAdd";
import GenreAutocomplete from "@/components/common/GenreAutocomplete";
import { strings } from "@/i18n/strings";

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
    control,
    formState: { errors },
  } = useForm<FormValues>();

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {strings.addText.title}
      </Typography>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          <Controller
            name="genre_name"
            control={control}
            rules={{ required: strings.addText.genreRequired }}
            render={({ field, fieldState }) => (
              <GenreAutocomplete
                value={field.value ?? ""}
                onChange={field.onChange}
                label={strings.common.genre}
                required
                error={!!fieldState.error}
                helperText={fieldState.error?.message}
              />
            )}
          />
          <TextField
            {...register("text", {
              required: strings.addText.textRequired,
              minLength: {
                value: 20,
                message: strings.addText.textMinLength,
              },
            })}
            label={strings.addText.textLabel}
            placeholder={strings.addText.textPlaceholder}
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
            {strings.addText.submit}
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
