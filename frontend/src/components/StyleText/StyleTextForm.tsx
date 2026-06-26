import { Controller, useForm } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormHelperText from "@mui/material/FormHelperText";
import CircularProgress from "@mui/material/CircularProgress";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import type { Author } from "@/types/author";
import type { StyleTextRequest } from "@/types/styleText";
import { formatAuthorLabel } from "./authorLabel";
import { strings } from "@/i18n/strings";

interface StyleTextFormProps {
  authors: Author[];
  isAuthorsLoading: boolean;
  onSubmit: (data: StyleTextRequest) => void;
  isLoading: boolean;
}

export default function StyleTextForm({
  authors,
  isAuthorsLoading,
  onSubmit,
  isLoading,
}: StyleTextFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<StyleTextRequest>({
    defaultValues: { author_id: "", text: "" },
  });

  const noAuthors = !isAuthorsLoading && authors.length === 0;

  return (
    <Paper sx={{ p: 3 }}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={2}>
          {isAuthorsLoading ? (
            <Stack direction="row" alignItems="center" spacing={1} sx={{ py: 1 }}>
              <CircularProgress size={22} />
              <FormHelperText>{strings.styleText.loadingAuthors}</FormHelperText>
            </Stack>
          ) : (
            <Controller
              name="author_id"
              control={control}
              rules={{
                required: strings.styleText.authorRequired,
              }}
              render={({ field }) => (
                <FormControl fullWidth error={!!errors.author_id} disabled={noAuthors}>
                  <InputLabel id="style-author-label">
                    {strings.styleText.authorLabel}
                  </InputLabel>
                  <Select
                    {...field}
                    labelId="style-author-label"
                    label={strings.styleText.authorLabel}
                  >
                    {authors.map((a) => (
                      <MenuItem key={a.id} value={a.id}>
                        {formatAuthorLabel(a)}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.author_id && (
                    <FormHelperText>{errors.author_id.message}</FormHelperText>
                  )}
                  {noAuthors && (
                    <FormHelperText>{strings.styleText.noGenerativeAuthors}</FormHelperText>
                  )}
                </FormControl>
              )}
            />
          )}

          <TextField
            {...register("text", {
              required: strings.styleText.textRequired,
              minLength: {
                value: 10,
                message: strings.styleText.textMinLength,
              },
            })}
            label={strings.styleText.textLabel}
            placeholder={strings.styleText.textPlaceholder}
            multiline
            minRows={6}
            maxRows={16}
            fullWidth
            error={!!errors.text}
            helperText={errors.text?.message}
          />

          <Button
            type="submit"
            variant="contained"
            size="large"
            loading={isLoading}
            disabled={isAuthorsLoading || noAuthors}
            endIcon={<AutoFixHighIcon />}
            sx={{ alignSelf: "flex-start" }}
          >
            {strings.styleText.submit}
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
