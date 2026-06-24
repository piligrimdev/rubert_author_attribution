import { lazy, Suspense } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import ScatterPlotIcon from "@mui/icons-material/ScatterPlot";
import type { EmbeddingUmapResponse } from "@/types/embeddingUmap";

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
          UMAP-проекция эмбеддингов
        </Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" paragraph>
        Двумерная проекция эмбеддингов текстов двух авторов (PCA → UMAP). Точки одного автора
        должны образовывать кластер — так видно, насколько стилистически различимы корпуса.
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
        <Chip label={`${data.meta.n_points} точек`} size="small" variant="outlined" />
        <Chip label={`${data.meta.n_authors} авторов`} size="small" variant="outlined" />
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
