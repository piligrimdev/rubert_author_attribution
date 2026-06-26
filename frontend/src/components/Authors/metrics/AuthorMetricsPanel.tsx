import { useMemo, useState } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid2";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import InsightsIcon from "@mui/icons-material/Insights";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTheme } from "@mui/material/styles";
import { METRIC_RU } from "@/constants/metricLabelsRu";
import {
  METRIC_BASE_KEYS,
  extractMetricStats,
  type AuthorMetricsResponse,
  type MetricBaseKey,
  type MetricQuartiles,
} from "@/types/authorMetrics";
import { useComputeAuthorMetricsPair } from "@/hooks/useAuthorMetrics";
import { useEmbeddingCompare } from "@/hooks/useEmbeddingCompare";
import { getEmbeddingCompareErrorMessage } from "@/utils/embeddingCompareError";
import type { Author } from "@/types/author";
import MetricBoxPlotSvg from "./MetricBoxPlotSvg";
import MetricMeanMedianBars from "./MetricMeanMedianBars";
import MetricMeanMedianCompareBars from "./MetricMeanMedianCompareBars";
import AuthorEmbeddingUmapSection from "./AuthorEmbeddingUmapSection";
import { format, strings } from "@/i18n/strings";

type Props = {
  authorId: string;
  textCount: number;
  /** Список авторов для выбора второго в сравнении (например, со страницы автора) */
  authorsForCompare?: Author[];
};

function formatAuthorOption(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}

function formatByMetric(base: string, v: number): string {
  if (base.includes("ratio") || base === "compression_ratio") {
    return v.toFixed(3);
  }
  if (
    base === "flesch_reading_ease" ||
    base === "gunning_fog" ||
    base === "mtld"
  ) {
    return v.toFixed(1);
  }
  return v.toFixed(2);
}

type SummaryRow = {
  key: MetricBaseKey;
  label: string;
  norm: number;
  mean: number;
  min: number;
  max: number;
};

type SummaryCompareRow = {
  key: MetricBaseKey;
  label: string;
  normA: number;
  normB: number;
  meanA: number;
  meanB: number;
  minA: number;
  maxA: number;
  minB: number;
  maxB: number;
};

/** Сводная горизонтальная диаграмма: положение среднего внутри диапазона min–max по корпусу. */
function SummaryMeanBarChart({ data }: { data: AuthorMetricsResponse }) {
  const theme = useTheme();
  const chartData = useMemo(() => {
    const rows: SummaryRow[] = [];
    for (const key of METRIC_BASE_KEYS) {
      const stats = extractMetricStats(data, key);
      if (!stats) continue;
      const { min, max, mean } = stats;
      const span = max - min || 1;
      const norm = ((mean - min) / span) * 100;
      rows.push({
        key,
        label: METRIC_RU[key].title,
        norm: Math.min(100, Math.max(0, norm)),
        mean,
        min,
        max,
      });
    }
    return rows;
  }, [data]);

  if (!chartData.length) return null;

  return (
    <Box sx={{ width: "100%", height: Math.max(300, chartData.length * 34 + 80) }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
        {strings.metrics.panel.summaryChartTitle}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 1 }}>
        {strings.metrics.panel.summaryChartHint}
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 8, right: 16, left: 4, bottom: 24 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(t) => `${t}%`}
            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={228}
            tick={{ fill: theme.palette.text.primary, fontSize: 11 }}
          />
          <Tooltip
            formatter={(value: number, _name: string, item) => {
              const p = item?.payload as SummaryRow;
              if (!p) return [String(value), ""];
              const unit = METRIC_RU[p.key].unitHint;
              return [
                `норм.: ${value.toFixed(0)}% · среднее: ${formatByMetric(p.key, p.mean)} · min: ${formatByMetric(p.key, p.min)} · max: ${formatByMetric(p.key, p.max)} (${unit})`,
                "",
              ];
            }}
          />
          <Bar
            dataKey="norm"
            name={strings.metrics.panel.meanPosition}
            fill={theme.palette.secondary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={22}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}

function SummaryMeanBarChartCompare({
  dataA,
  dataB,
  labelA,
  labelB,
}: {
  dataA: AuthorMetricsResponse;
  dataB: AuthorMetricsResponse;
  labelA: string;
  labelB: string;
}) {
  const theme = useTheme();
  const chartData = useMemo(() => {
    const rows: SummaryCompareRow[] = [];
    for (const key of METRIC_BASE_KEYS) {
      const sa = extractMetricStats(dataA, key);
      const sb = extractMetricStats(dataB, key);
      if (!sa || !sb) continue;
      const spanA = sa.max - sa.min || 1;
      const spanB = sb.max - sb.min || 1;
      const normA = ((sa.mean - sa.min) / spanA) * 100;
      const normB = ((sb.mean - sb.min) / spanB) * 100;
      rows.push({
        key,
        label: METRIC_RU[key].title,
        normA: Math.min(100, Math.max(0, normA)),
        normB: Math.min(100, Math.max(0, normB)),
        meanA: sa.mean,
        meanB: sb.mean,
        minA: sa.min,
        maxA: sa.max,
        minB: sb.min,
        maxB: sb.max,
      });
    }
    return rows;
  }, [dataA, dataB]);

  if (!chartData.length) return null;

  return (
    <Box sx={{ width: "100%", height: Math.max(320, chartData.length * 36 + 96) }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
        {strings.metrics.panel.summaryCompareTitle}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 1 }}>
        {strings.metrics.panel.summaryCompareHint}
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 8, right: 16, left: 4, bottom: 24 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(t) => `${t}%`}
            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={228}
            tick={{ fill: theme.palette.text.primary, fontSize: 11 }}
          />
          <Tooltip
            formatter={(value: number, name: string, item) => {
              const p = item?.payload as SummaryCompareRow;
              if (!p) return [String(value), name];
              const unit = METRIC_RU[p.key].unitHint;
              const isA = name === labelA;
              const mean = isA ? p.meanA : p.meanB;
              const lo = isA ? p.minA : p.minB;
              const hi = isA ? p.maxA : p.maxB;
              return [
                `норм.: ${value.toFixed(0)}% · среднее: ${formatByMetric(p.key, mean)} · min: ${formatByMetric(p.key, lo)} · max: ${formatByMetric(p.key, hi)} (${unit})`,
                "",
              ];
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar
            dataKey="normA"
            name={labelA}
            fill={theme.palette.primary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={20}
          />
          <Bar
            dataKey="normB"
            name={labelB}
            fill={theme.palette.secondary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={20}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}

function MetricDeltasBlock({
  statsA,
  statsB,
  fmt,
  nameA,
  nameB,
}: {
  statsA: MetricQuartiles;
  statsB: MetricQuartiles;
  fmt: (v: number) => string;
  nameA: string;
  nameB: string;
}) {
  const d = (a: number, b: number) => b - a;
  const line = (title: string, delta: number) => (
    <Typography key={title} variant="caption" component="div" sx={{ display: "block" }}>
      Δ {title} ({nameB} − {nameA}):{" "}
      <Box component="span" sx={{ fontWeight: 600 }}>
        {delta >= 0 ? "+" : ""}
        {fmt(delta)}
      </Box>
    </Typography>
  );
  return (
    <Box
      sx={{
        bgcolor: "action.hover",
        borderRadius: 1,
        p: 1.25,
        border: 1,
        borderColor: "divider",
      }}
    >
      <Typography variant="caption" fontWeight={700} display="block" sx={{ mb: 0.75 }}>
        {format(strings.metrics.panel.deltaTitle, { nameA, nameB })}
      </Typography>
      {line(strings.metrics.panel.mean, d(statsA.mean, statsB.mean))}
      {line(strings.metrics.panel.median, d(statsA.median, statsB.median))}
      {line("Q1", d(statsA.q25, statsB.q25))}
      {line("Q3", d(statsA.q75, statsB.q75))}
      {line(strings.metrics.panel.minimum, d(statsA.min, statsB.min))}
      {line(strings.metrics.panel.maximum, d(statsA.max, statsB.max))}
    </Box>
  );
}

function authorLabel(
  data: AuthorMetricsResponse | null | undefined,
  fallback: string,
): string {
  if (data && typeof data.author === "string" && data.author.trim()) return data.author;
  return fallback;
}

export default function AuthorMetricsPanel({
  authorId,
  textCount,
  authorsForCompare,
}: Props) {
  const mutation = useComputeAuthorMetricsPair();
  const embeddingCompare = useEmbeddingCompare();
  const data = mutation.data?.primary;
  const secondary = mutation.data?.secondary;
  const [compareAuthor, setCompareAuthor] = useState<Author | null>(null);

  const compareOptions = useMemo(
    () => (authorsForCompare ?? []).filter((a) => a.id !== authorId),
    [authorsForCompare, authorId],
  );

  const isComparing = Boolean(compareAuthor);
  const isPending =
    mutation.isPending || (isComparing && embeddingCompare.isPending);

  const handleCompute = () => {
    mutation.mutate({
      primaryId: authorId,
      compareId: compareAuthor?.id ?? null,
    });
    if (compareAuthor) {
      embeddingCompare.mutate({
        author_id_1: authorId,
        author_id_2: compareAuthor.id,
        max_per_author: 50,
      });
    } else {
      embeddingCompare.reset();
    }
  };

  const primaryName = authorLabel(data, strings.metrics.panel.primaryAuthorFallback);
  const secondaryName = authorLabel(secondary, strings.metrics.panel.secondaryAuthorFallback);

  return (
    <Paper sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
        <InsightsIcon color="primary" />
        <Typography variant="h6">{strings.metrics.panel.title}</Typography>
      </Stack>
      <Divider sx={{ mb: 2 }} />

      <Typography variant="body2" color="text.secondary" paragraph>
        {strings.metrics.panel.description}
      </Typography>

      <Stack spacing={2} alignItems="stretch">
        {compareOptions.length > 0 && (
            <Autocomplete
            options={compareOptions}
            value={compareAuthor}
            onChange={(_, v) => {
              setCompareAuthor(v);
              embeddingCompare.reset();
            }}
            getOptionLabel={(o) => formatAuthorOption(o)}
            renderInput={(params) => (
              <TextField
                {...params}
                label={strings.metrics.panel.compareLabel}
                placeholder={strings.metrics.panel.comparePlaceholder}
                size="small"
              />
            )}
          />
        )}
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-start">
          <Button
            variant="contained"
            onClick={handleCompute}
            disabled={isPending || textCount === 0}
          >
            {isPending
              ? strings.metrics.panel.computing
              : compareAuthor
                ? strings.metrics.panel.computeCompare
                : strings.metrics.panel.compute}
          </Button>
          {textCount === 0 && (
            <Typography variant="body2" color="warning.main">
              {strings.metrics.panel.noTextsWarning}
            </Typography>
          )}
        </Stack>
      </Stack>

      {mutation.isPending && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {mutation.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {format(strings.metrics.panel.loadError, { message: mutation.error.message })}
        </Alert>
      )}

      {embeddingCompare.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {getEmbeddingCompareErrorMessage(embeddingCompare.error)}
        </Alert>
      )}

      {data && !mutation.isPending && (
        <Stack spacing={3} sx={{ mt: 3 }}>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
            <Typography variant="body2">
              <strong>{primaryName}</strong>
              {typeof data.text_count === "number"
                ? format(strings.metrics.panel.textsInCalc, { count: data.text_count })
                : ""}
            </Typography>
            {secondary && (
              <Typography variant="body2">
                <strong>{secondaryName}</strong>
                {typeof secondary.text_count === "number"
                  ? format(strings.metrics.panel.textsInCalc, { count: secondary.text_count })
                  : ""}
              </Typography>
            )}
          </Stack>

          {secondary ? (
            <SummaryMeanBarChartCompare
              dataA={data}
              dataB={secondary}
              labelA={primaryName}
              labelB={secondaryName}
            />
          ) : (
            <SummaryMeanBarChart data={data} />
          )}

          <Typography variant="subtitle1" sx={{ fontWeight: 600, pt: 1 }}>
            {strings.metrics.panel.detailTitle}
          </Typography>

          <Grid container spacing={2}>
            {METRIC_BASE_KEYS.map((base) => {
              const meta = METRIC_RU[base];
              const statsA = extractMetricStats(data, base);
              const statsB = secondary ? extractMetricStats(secondary, base) : null;
              const fmt = (v: number) => formatByMetric(base, v);
              return (
                <Grid key={base} size={{ xs: 12, md: 6 }}>
                  <Paper variant="outlined" sx={{ p: 2, height: "100%" }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {meta.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {meta.description}
                    </Typography>
                    <Typography variant="caption" color="text.disabled" display="block" sx={{ mb: 1 }}>
                      {format(strings.metrics.panel.units, { unit: meta.unitHint })}
                    </Typography>
                    {!statsA ? (
                      <Typography color="text.secondary">
                        {strings.metrics.panel.noData}
                      </Typography>
                    ) : statsB && secondary ? (
                      <Stack spacing={2}>
                        <Stack
                          direction={{ xs: "column", sm: "row" }}
                          spacing={2}
                          alignItems="flex-start"
                        >
                          <Box sx={{ flex: 1, minWidth: 0, width: "100%" }}>
                            <Typography variant="caption" color="primary" fontWeight={700}>
                              {primaryName}
                            </Typography>
                            <MetricBoxPlotSvg stats={statsA} formatTick={fmt} colorVariant="primary" />
                          </Box>
                          <Box sx={{ flex: 1, minWidth: 0, width: "100%" }}>
                            <Typography variant="caption" color="secondary" fontWeight={700}>
                              {secondaryName}
                            </Typography>
                            <MetricBoxPlotSvg stats={statsB} formatTick={fmt} colorVariant="secondary" />
                          </Box>
                        </Stack>
                        <MetricMeanMedianCompareBars
                          statsA={statsA}
                          statsB={statsB}
                          labelA={primaryName}
                          labelB={secondaryName}
                          formatValue={fmt}
                        />
                        <MetricDeltasBlock
                          statsA={statsA}
                          statsB={statsB}
                          fmt={fmt}
                          nameA={primaryName}
                          nameB={secondaryName}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {format(strings.metrics.panel.compareStatsLine, {
                            nameA: primaryName,
                            meanA: fmt(statsA.mean),
                            stdA: formatStd(data, base, fmt),
                            nameB: secondaryName,
                            meanB: fmt(statsB.mean),
                            stdB: formatStd(secondary, base, fmt),
                          })}
                        </Typography>
                      </Stack>
                    ) : (
                      <Stack spacing={2}>
                        <Box>
                          <Typography variant="caption" color="text.secondary" fontWeight={600}>
                            {strings.metrics.panel.boxplotTitle}
                          </Typography>
                          <MetricBoxPlotSvg stats={statsA} formatTick={fmt} />
                        </Box>
                        <MetricMeanMedianBars stats={statsA} formatValue={fmt} />
                        <Typography variant="caption" color="text.secondary">
                          {format(strings.metrics.panel.statsLine, {
                            mean: fmt(statsA.mean),
                            std: formatStd(data, base, fmt),
                          })}
                        </Typography>
                      </Stack>
                    )}
                  </Paper>
                </Grid>
              );
            })}
          </Grid>

          {embeddingCompare.data && compareAuthor && (
            <AuthorEmbeddingUmapSection data={embeddingCompare.data} />
          )}
        </Stack>
      )}
    </Paper>
  );
}

function formatStd(
  data: AuthorMetricsResponse,
  base: string,
  fmt: (v: number) => string,
): string {
  const v = data[`${base}_std`];
  let n: number | undefined;
  if (typeof v === "number" && Number.isFinite(v)) n = v;
  else if (typeof v === "string") {
    const p = Number(v);
    if (Number.isFinite(p)) n = p;
  }
  return n !== undefined ? fmt(n) : strings.common.dash;
}
