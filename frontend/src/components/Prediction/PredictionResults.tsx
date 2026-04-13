import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Fade from "@mui/material/Fade";
import Stack from "@mui/material/Stack";
import type { PredictionResponse } from "@/types/prediction";
import PredictionResultItem from "./PredictionResultItem";

interface PredictionResultsProps {
  data: PredictionResponse;
}

export default function PredictionResults({ data }: PredictionResultsProps) {
  const items = data.items;

  if (!items.length) {
    return (
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography color="text.secondary">
          Похожих текстов не найдено.
        </Typography>
      </Paper>
    );
  }

  return (
    <Fade in>
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Ближайшие тексты
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
