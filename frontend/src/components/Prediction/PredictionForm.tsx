import { Controller, useForm, useWatch } from "react-hook-form";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Slider from "@mui/material/Slider";
import SendIcon from "@mui/icons-material/Send";
import type {
  AttributionFormMode,
  AttributionSubmitPayload,
} from "@/types/prediction";

type PredictionFormFields = {
  text: string;
  k: number;
  mode: AttributionFormMode;
  threshold: number;
};

interface PredictionFormProps {
  selectedAuthorIds: string[];
  isAuthorsLoading: boolean;
  onSubmit: (data: AttributionSubmitPayload) => void;
  isLoading: boolean;
}

export default function PredictionForm({
  selectedAuthorIds,
  isAuthorsLoading,
  onSubmit,
  isLoading,
}: PredictionFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<PredictionFormFields>({
    defaultValues: {
      k: 5,
      text: "",
      mode: "nearest",
      threshold: 0.5,
    },
  });

  const mode = useWatch({ control, name: "mode" });

  const handleValidSubmit = (fields: PredictionFormFields) => {
    const { mode: submitMode, threshold, ...rest } = fields;
    const base = {
      ...rest,
      ...(selectedAuthorIds.length ? { author_ids: selectedAuthorIds } : {}),
    };
    if (submitMode === "nearest") {
      onSubmit({ mode: "nearest", data: base });
    } else {
      onSubmit({ mode: "voting", data: { ...base, threshold } });
    }
  };

  return (
    <Paper sx={{ p: 3, flex: 1, minWidth: 0 }}>
      <form onSubmit={handleSubmit(handleValidSubmit)} noValidate>
        <Stack spacing={2}>
          <Controller
            name="mode"
            control={control}
            render={({ field }) => (
              <Stack spacing={0.5}>
                <Typography variant="subtitle2" color="text.secondary">
                  Метод
                </Typography>
                <ToggleButtonGroup
                  value={field.value}
                  exclusive
                  fullWidth
                  ref={field.ref}
                  onChange={(_, value: AttributionFormMode | null) => {
                    if (value != null) field.onChange(value);
                  }}
                  aria-label="метод атрибуции"
                >
                  <ToggleButton value="nearest" aria-label="Ближайшие эмбеддинги">
                    Ближайшие эмбеддинги
                  </ToggleButton>
                  <ToggleButton value="voting" aria-label="Голосование по порогу">
                    Голосование (порог)
                  </ToggleButton>
                </ToggleButtonGroup>
                <Typography variant="caption" color="text.secondary">
                  {field.value === "nearest"
                    ? "Только список k ближайших фрагментов в базе."
                    : "Учитываются голоса среди соседей; автор фиксируется, если сходство с ближайшим выше порога."}
                </Typography>
              </Stack>
            )}
          />

          {mode === "voting" && (
            <Controller
              name="threshold"
              control={control}
              rules={{
                min: { value: 0.01, message: "Минимум 0.01" },
                max: { value: 1, message: "Максимум 1" },
              }}
              render={({ field, fieldState }) => (
                <Stack spacing={1}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Порог схожести (косинус ближайшего соседа)
                  </Typography>
                  <Slider
                    value={field.value}
                    onChange={(_, v) =>
                      field.onChange(Array.isArray(v) ? v[0] : v)
                    }
                    min={0.01}
                    max={1}
                    step={0.01}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(v) => `${(v * 100).toFixed(0)}%`}
                    marks={[
                      { value: 0.25, label: "25%" },
                      { value: 0.5, label: "50%" },
                      { value: 0.75, label: "75%" },
                    ]}
                  />
                  {fieldState.error && (
                    <Typography variant="caption" color="error">
                      {fieldState.error.message}
                    </Typography>
                  )}
                </Stack>
              )}
            />
          )}

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
            label="Количество ближайших текстов (k)"
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
            disabled={isAuthorsLoading}
            endIcon={<SendIcon />}
            sx={{ alignSelf: "flex-start" }}
          >
            {mode === "nearest" ? "Найти ближайшие" : "Атрибутировать"}
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
