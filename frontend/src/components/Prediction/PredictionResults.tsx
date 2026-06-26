import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Fade from "@mui/material/Fade";
import Stack from "@mui/material/Stack";
import type { NearestTextsResponse } from "@/types/prediction";
import PredictionResultItem from "./PredictionResultItem";
import { strings } from "@/i18n/strings";

interface PredictionResultsProps {
  data: NearestTextsResponse;
}

export default function PredictionResults({ data }: PredictionResultsProps) {
  const items = data.items;

  if (!items.length) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">
          {strings.attribution.noSimilarTexts}
        </Typography>
      </Paper>
    );
  }

  return (
    <Fade in>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          {strings.attribution.nearestTexts}
        </Typography>
        <Divider sx={{ mb: 1 }} />
        <Stack divider={<Divider />}>
          {items.map((item, idx) => (
            <PredictionResultItem key={item.text_id} item={item} rank={idx + 1} />
          ))}
        </Stack>
      </Paper>
    </Fade>
  );
}
