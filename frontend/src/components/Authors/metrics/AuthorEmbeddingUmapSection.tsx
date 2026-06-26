import { lazy, Suspense } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import ScatterPlotIcon from "@mui/icons-material/ScatterPlot";
import type { EmbeddingUmapResponse } from "@/types/embeddingUmap";
import { format, strings } from "@/i18n/strings";

const EmbeddingUmapPlot = lazy(
  () => import("@/components/Embeddings/EmbeddingUmapPlot"),
);

type Props = {
  data: EmbeddingUmapResponse;
};

export default function AuthorEmbeddingUmapSection({ data }: Props) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <ScatterPlotIcon color="primary" fontSize="small" />
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {strings.metrics.umap.title}
        </Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" paragraph>
        {strings.metrics.umap.description}
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
        <Chip
          label={format(strings.metrics.umap.points, { count: data.meta.n_points })}
          size="small"
          variant="outlined"
        />
        <Chip
          label={format(strings.metrics.umap.authors, { count: data.meta.n_authors })}
          size="small"
          variant="outlined"
        />
      </Stack>
      <Suspense
        fallback={
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        }
      >
        <EmbeddingUmapPlot data={data} />
      </Suspense>
    </Paper>
  );
}
