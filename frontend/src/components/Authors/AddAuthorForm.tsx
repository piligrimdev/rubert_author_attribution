import { useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import SaveIcon from "@mui/icons-material/Save";
import type { CreateAuthorRequest } from "@/types/author";
import { strings } from "@/i18n/strings";

interface AddAuthorFormProps {
  onSubmit: (data: CreateAuthorRequest) => void;
  isLoading: boolean;
}

export default function AddAuthorForm({ onSubmit, isLoading }: AddAuthorFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateAuthorRequest>();

  return (
    <Paper sx={{ p: 3 }}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={3}>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              {...register("surname", { required: strings.authors.surnameRequired })}
              label={strings.common.surname}
              fullWidth
              error={!!errors.surname}
              helperText={errors.surname?.message}
            />
            <TextField
              {...register("name", { required: strings.authors.nameRequired })}
              label={strings.common.name}
              fullWidth
              error={!!errors.name}
              helperText={errors.name?.message}
            />
            <TextField
              {...register("last_name", { required: strings.authors.lastNameRequired })}
              label={strings.common.lastName}
              fullWidth
              error={!!errors.last_name}
              helperText={errors.last_name?.message}
            />
          </Stack>

          <Button
            type="submit"
            variant="contained"
            size="large"
            loading={isLoading}
            startIcon={<SaveIcon />}
            sx={{ alignSelf: "flex-start" }}
          >
            {strings.authors.createAuthor}
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
