import Stack from "@mui/material/Stack";
import PageTitle from "@/components/common/PageTitle";
import PredictionForm from "@/components/Prediction/PredictionForm";
import PredictionResults from "@/components/Prediction/PredictionResults";
import PredictionError from "@/components/Prediction/PredictionError";
import { usePrediction } from "@/hooks/usePrediction";
import type { PredictRequest } from "@/types/prediction";

export default function HomePage() {
  const { mutate, data, error, isPending } = usePrediction();

  const handleSubmit = (form: PredictRequest) => {
    mutate(form);
  };

  return (
    <Stack spacing={2}>
      <PageTitle subtitle="Определение автора текста на основе стилистического анализа">
        Атрибуция авторства
      </PageTitle>

      <PredictionForm onSubmit={handleSubmit} isLoading={isPending} />

      {error && <PredictionError error={error} />}
      {data && <PredictionResults data={data} />}
    </Stack>
  );
}
