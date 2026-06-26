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
import { format, strings } from "@/i18n/strings";

function authorLabelForId(authorId: string, items: NearestTextItem[]): string {
  const hit = items.find((i) => i.author_id === authorId);
  return hit?.author ?? authorId;
}

function formatFiniteOrDash(
  value: number | null | undefined,
  toFixedDigits: number,
): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return strings.common.dash;
  }
  return value.toFixed(toFixedDigits);
}

function confidencePercentLabel(
  confidence: number | null | undefined,
): string {
  if (typeof confidence !== "number" || !Number.isFinite(confidence)) {
    return strings.attribution.confidenceEmpty;
  }
  return format(strings.attribution.confidence, {
    value: (confidence * 100).toFixed(1),
  });
}

function shouldShowVotingResult(data: VotesResponse): boolean {
  const hasAvgSim =
    typeof data.avg_sim === "number" && Number.isFinite(data.avg_sim);
  const hasDistance = data.items.some(
    (item) => typeof item.distance === "number" && Number.isFinite(item.distance),
  );
  return hasAvgSim && hasDistance;
}

interface Props {
  data: VotesResponse;
}

export default function AttributionVoteResults({ data }: Props) {
  const { predicted, confidence, avg_sim, votes, items } = data;
  const sortedVotes = Object.entries(votes).sort((a, b) => b[1] - a[1]);
  const showVotingResult = shouldShowVotingResult(data);

  return (
    <Fade in>
      <Stack spacing={2}>
        {showVotingResult &&
          (predicted ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {strings.attribution.votingResult}
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              {strings.attribution.predictedAuthor}{" "}
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
                label={format(strings.attribution.avgDistance, {
                  value: formatFiniteOrDash(avg_sim, 4),
                })}
                variant="outlined"
                size="small"
              />
              <Button
                component={RouterLink}
                to={`/authors/${predicted}`}
                size="small"
                variant="outlined"
              >
                {strings.attribution.authorPage}
              </Button>
            </Stack>
            {sortedVotes.length > 0 && (
              <>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {strings.attribution.votesTitle}
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
              {strings.attribution.thresholdWarning}
            </Typography>
          </Alert>
        ))}

        {items.length > 0 ? (
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
        ) : (
          <Paper sx={{ p: 3 }}>
            <Typography color="text.secondary">
              {strings.attribution.noSimilarTexts}
            </Typography>
          </Paper>
        )}
      </Stack>
    </Fade>
  );
}
