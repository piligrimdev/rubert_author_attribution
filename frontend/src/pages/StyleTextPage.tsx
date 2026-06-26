import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import PageTitle from "@/components/common/PageTitle";
import StyleTextForm from "@/components/StyleText/StyleTextForm";
import StyleTextResult from "@/components/StyleText/StyleTextResult";
import PredictionError from "@/components/Prediction/PredictionError";
import { useGenerativeAuthors } from "@/hooks/useGenerativeAuthors";
import { useStyleText } from "@/hooks/useStyleText";
import type { StyleTextRequest } from "@/types/styleText";
import { strings } from "@/i18n/strings";

export default function StyleTextPage() {
  const { data: authors = [], isLoading: authorsLoading, error: authorsError } =
    useGenerativeAuthors();
  const { mutate, data, error, isPending } = useStyleText();

  const handleSubmit = (form: StyleTextRequest) => {
    mutate(form);
  };

  return (
    <Stack spacing={2}>
      <PageTitle subtitle={strings.styleText.subtitle}>
        {strings.styleText.title}
      </PageTitle>

      {authorsError && (
        <Alert severity="error">{strings.styleText.authorsLoadError}</Alert>
      )}

      <StyleTextForm
        authors={authors}
        isAuthorsLoading={authorsLoading}
        onSubmit={handleSubmit}
        isLoading={isPending}
      />

      {error && <PredictionError error={error} />}
      {data?.text != null && data.text !== "" && (
        <StyleTextResult text={data.text} />
      )}
    </Stack>
  );
}
