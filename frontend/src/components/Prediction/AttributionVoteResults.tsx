import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Fade from "@mui/material/Fade";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import { Link as RouterLink } from "react-router-dom";
import Link from "@mui/material/Link";
import Chip from "@mui/material/Chip";
import type { NearestTextItem, VotesResponse } from "@/types/prediction";
import PredictionResultItem from "./PredictionResultItem";

function authorLabelForId(authorId: string, items: NearestTextItem[]): string {
  const hit = items.find((i) => i.author_id === authorId);
  return hit?.author ?? authorId;
}

/** Безопасно для ответов API с null / NaN (например, без валидных distance). */
function formatFiniteOrDash(
  value: number | null | undefined,
  toFixedDigits: number,
): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "—";
  }
  return value.toFixed(toFixedDigits);
}

function confidencePercentLabel(
  confidence: number | null | undefined,
): string {
  if (typeof confidence !== "number" || !Number.isFinite(confidence)) {
    return "Сходство с ближайшим: —";
  }
  return `Сходство с ближайшим: ${(confidence * 100).toFixed(1)} %`;
}

interface Props {
  data: VotesResponse;
}

export default function AttributionVoteResults({ data }: Props) {
  const { predicted, confidence, avg_sim, votes, items } = data;
  const sortedVotes = Object.entries(votes).sort((a, b) => b[1] - a[1]);

  return (
    <Fade in>
      <Stack spacing={2}>
        {predicted ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Результат голосования
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              Предполагаемый автор:{" "}
              <Link
                component={RouterLink}
                to={`/authors/${predicted}`}
                fontWeight={700}
                underline="hover"
              >
                {authorLabelForId(predicted, items)}
              </Link>
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
              <Chip
                label={confidencePercentLabel(confidence)}
                color="primary"
                size="small"
              />
              <Chip
                label={`Среднее расстояние до k соседей: ${formatFiniteOrDash(avg_sim, 4)}`}
                variant="outlined"
                size="small"
              />
              <Button
                component={RouterLink}
                to={`/authors/${predicted}`}
                size="small"
                variant="outlined"
              >
                Страница автора
              </Button>
            </Stack>
            {sortedVotes.length > 0 && (
              <>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Голоса среди ближайших фрагментов
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {sortedVotes.map(([authorId, count]) => (
                    <Chip
                      key={authorId}
                      label={`${authorLabelForId(authorId, items)}: ${count}`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Stack>
              </>
            )}
          </Paper>
        ) : (
          <Alert severity="warning" sx={{ alignItems: "flex-start" }}>
            <Typography variant="body2" component="div">
              Вероятно, автор фрагмента неизвестен модели или лучшее совпадение не проходит выбранный
              порог схожести. Попробуйте изменить параметры:{" "}
              <strong>k</strong>, набор <strong>авторов</strong> для сравнения,{" "}
              <strong>порог</strong> или сам <strong>текст</strong> (длину и содержание).
            </Typography>
          </Alert>
        )}

        {items.length > 0 ? (
          <Paper sx={{ p: 3 }}>
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
        ) : (
          <Paper sx={{ p: 3 }}>
            <Typography color="text.secondary">Похожих текстов не найдено.</Typography>
          </Paper>
        )}
      </Stack>
    </Fade>
  );
}
