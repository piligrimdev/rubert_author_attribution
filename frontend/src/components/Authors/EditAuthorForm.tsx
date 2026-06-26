import { useEffect } from "react";
import { useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import SaveIcon from "@mui/icons-material/Save";
import CloseIcon from "@mui/icons-material/Close";
import type { Author, EditAuthorRequest } from "@/types/author";
import {
  buildAuthorEditPatch,
  type AuthorEditFormValues,
} from "@/utils/authorEditPatch";
import { strings } from "@/i18n/strings";

interface EditAuthorFormProps {
  author: Author;
  onSubmit: (data: EditAuthorRequest) => void;
  onCancel: () => void;
  isLoading: boolean;
}

function toFormValues(author: Author): AuthorEditFormValues {
  return {
    surname: author.surname ?? "",
    name: author.name ?? "",
    last_name: author.last_name ?? "",
    description: author.description ?? "",
  };
}

export default function EditAuthorForm({
  author,
  onSubmit,
  onCancel,
  isLoading,
}: EditAuthorFormProps) {
  const { register, handleSubmit, reset } = useForm<AuthorEditFormValues>({
    defaultValues: toFormValues(author),
  });

  useEffect(() => {
    reset(toFormValues(author));
  }, [author, reset]);

  const handleFormSubmit = (values: AuthorEditFormValues) => {
    onSubmit(buildAuthorEditPatch(author, values));
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      <Stack spacing={2}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <TextField
            {...register("surname")}
            label={strings.common.surname}
            fullWidth
          />
          <TextField
            {...register("name")}
            label={strings.common.name}
            fullWidth
          />
          <TextField
            {...register("last_name")}
            label={strings.common.lastName}
            fullWidth
          />
        </Stack>
        <TextField
          {...register("description")}
          label={strings.common.description}
          fullWidth
          multiline
          minRows={3}
        />
        <Stack direction="row" spacing={1}>
          <Button
            type="submit"
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={isLoading}
          >
            {strings.common.save}
          </Button>
          <Button
            type="button"
            variant="outlined"
            startIcon={<CloseIcon />}
            onClick={onCancel}
            disabled={isLoading}
          >
            {strings.common.cancel}
          </Button>
        </Stack>
      </Stack>
    </form>
  );
}
