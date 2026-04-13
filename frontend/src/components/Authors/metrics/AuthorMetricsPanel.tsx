import { useMemo } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid2";
import InsightsIcon from "@mui/icons-material/Insights";
import {
  Bar,
  BarChart,
  CartesianGrid,
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
} from "@/types/authorMetrics";
import { useComputeAuthorMetrics } from "@/hooks/useAuthorMetrics";
import MetricBoxPlotSvg from "./MetricBoxPlotSvg";
import MetricMeanMedianBars from "./MetricMeanMedianBars";

type Props = {
  authorId: string;
  textCount: number;
};

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
  key: (typeof METRIC_BASE_KEYS)[number];
  label: string;
  norm: number;
  mean: number;
  min: number;
  max: number;
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
        Сводная столбчатая диаграмма (нормализация)
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 1 }}>
        Длина полосы показывает, где среднее значение лежит между минимумом и максимумом по
        всем текстам автора (100% — у максимума, 0% — у минимума). Так можно сравнить профили
        разных метрик на одном графике, не смешивая реальные единицы измерения.
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
            name="Положение среднего"
            fill={theme.palette.secondary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={22}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}

export default function AuthorMetricsPanel({ authorId, textCount }: Props) {
  const mutation = useComputeAuthorMetrics();
  const data = mutation.data;

  const handleCompute = () => {
    mutation.mutate(authorId);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
        <InsightsIcon color="primary" />
        <Typography variant="h6">Стилистические метрики текстов</Typography>
      </Stack>
      <Divider sx={{ mb: 2 }} />

      <Typography variant="body2" color="text.secondary" paragraph>
        Метрики считаются по сохранённым текстам автора (до 50 фрагментов). Ящик с усами
        показывает разброс по текстам: нижний и верхний усы — минимум и максимум, прямоугольник
        — от 25-го до 75-го перцентиля, жирная линия — медиана. Рядом — столбчатая диаграмма
        среднего и медианы.
      </Typography>

      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-start">
        <Button
          variant="contained"
          onClick={handleCompute}
          disabled={mutation.isPending || textCount === 0}
        >
          {mutation.isPending ? "Считаем…" : "Рассчитать метрики"}
        </Button>
        {textCount === 0 && (
          <Typography variant="body2" color="warning.main">
            Нет текстов у автора — добавьте хотя бы один текст, чтобы запустить расчёт.
          </Typography>
        )}
      </Stack>

      {mutation.isPending && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {mutation.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Не удалось получить метрики: {mutation.error.message}
        </Alert>
      )}

      {data && !mutation.isPending && (
        <Stack spacing={3} sx={{ mt: 3 }}>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
            <Typography variant="body2">
              <strong>Автор в ответе API:</strong>{" "}
              {typeof data.author === "string" ? data.author : "—"}
            </Typography>
            <Typography variant="body2">
              <strong>Число текстов в расчёте:</strong>{" "}
              {typeof data.text_count === "number" ? data.text_count : "—"}
            </Typography>
          </Stack>

          <SummaryMeanBarChart data={data} />

          <Typography variant="subtitle1" sx={{ fontWeight: 600, pt: 1 }}>
            Подробно по каждой метрике
          </Typography>

          <Grid container spacing={2}>
            {METRIC_BASE_KEYS.map((base) => {
              const meta = METRIC_RU[base];
              const stats = extractMetricStats(data, base);
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
                      Единицы: {meta.unitHint}
                    </Typography>
                    {!stats ? (
                      <Typography color="text.secondary">Нет данных по этой метрике</Typography>
                    ) : (
                      <Stack spacing={2}>
                        <Box>
                          <Typography variant="caption" color="text.secondary" fontWeight={600}>
                            Ящик с усами (по текстам автора)
                          </Typography>
                          <MetricBoxPlotSvg stats={stats} formatTick={fmt} />
                        </Box>
                        <MetricMeanMedianBars stats={stats} formatValue={fmt} />
                        <Typography variant="caption" color="text.secondary">
                          Среднее: {fmt(stats.mean)}, СКО:{" "}
                          {formatStd(data, base, fmt)}
                        </Typography>
                      </Stack>
                    )}
                  </Paper>
                </Grid>
              );
            })}
          </Grid>
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
  return n !== undefined ? fmt(n) : "—";
}
