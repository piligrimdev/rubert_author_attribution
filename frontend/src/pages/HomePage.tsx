import { useState } from "react";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import PageTitle from "@/components/common/PageTitle";
import PredictionForm from "@/components/Prediction/PredictionForm";
import PredictionAuthorsSidebar from "@/components/Prediction/PredictionAuthorsSidebar";
import PredictionResults from "@/components/Prediction/PredictionResults";
import AttributionVoteResults from "@/components/Prediction/AttributionVoteResults";
import PredictionError from "@/components/Prediction/PredictionError";
import {
  useNearestKMutation,
  useAttributeMutation,
} from "@/hooks/usePrediction";
import { useAuthors } from "@/hooks/useAuthors";
import type { AttributionSubmitPayload } from "@/types/prediction";
import { strings } from "@/i18n/strings";

export default function HomePage() {
  const [selectedAuthorIds, setSelectedAuthorIds] = useState<string[]>([]);
  const nearest = useNearestKMutation();
  const attribute = useAttributeMutation();
  const {
    data: authors = [],
    isLoading: authorsLoading,
    error: authorsError,
  } = useAuthors();

  const handleSubmit = (payload: AttributionSubmitPayload) => {
    if (payload.mode === "nearest") {
      attribute.reset();
      nearest.mutate(payload.data);
    } else {
      nearest.reset();
      attribute.mutate(payload.data);
    }
  };

  const isPending = nearest.isPending || attribute.isPending;
  const error = nearest.error ?? attribute.error;

  return (
    <Stack spacing={2}>
      <PageTitle subtitle={strings.home.subtitle}>
        {strings.home.title}
      </PageTitle>

      {authorsError && (
        <Alert severity="error">{strings.home.authorsLoadError}</Alert>
      )}

      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          alignItems: { xs: "stretch", md: "flex-start" },
          gap: 2,
        }}
      >
        <PredictionAuthorsSidebar
          authors={authors}
          selectedIds={selectedAuthorIds}
          onSelectionChange={setSelectedAuthorIds}
          isLoading={authorsLoading}
        />

        <Stack spacing={2} sx={{ flex: 1, minWidth: 0 }}>
          <PredictionForm
            selectedAuthorIds={selectedAuthorIds}
            isAuthorsLoading={authorsLoading}
            onSubmit={handleSubmit}
            isLoading={isPending}
          />

          {error && <PredictionError error={error} />}
          {nearest.data && <PredictionResults data={nearest.data} />}
          {attribute.data && <AttributionVoteResults data={attribute.data} />}
        </Stack>
      </Box>
    </Stack>
  );
}
