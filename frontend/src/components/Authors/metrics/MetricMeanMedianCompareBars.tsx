import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
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
import type { MetricQuartiles } from "@/types/authorMetrics";

type Props = {
  statsA: MetricQuartiles;
  statsB: MetricQuartiles;
  labelA: string;
  labelB: string;
  formatValue?: (v: number) => string;
};

/** Два автора рядом по категориям «Среднее» и «Медиана»; общая числовая ось. */
export default function MetricMeanMedianCompareBars({
  statsA,
  statsB,
  labelA,
  labelB,
  formatValue,
}: Props) {
  const theme = useTheme();
  const fmt = formatValue ?? ((v: number) => String(v));
  const values = [
    statsA.min,
    statsA.max,
    statsA.mean,
    statsA.median,
    statsB.min,
    statsB.max,
    statsB.mean,
    statsB.median,
  ];
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const pad = (hi - lo) * 0.08 || 0.01;
  const domain: [number, number] = [lo - pad, hi + pad];

  const keyA = "a";
  const keyB = "b";

  const data = [
    { name: "Среднее", [keyA]: statsA.mean, [keyB]: statsB.mean },
    { name: "Медиана", [keyA]: statsA.median, [keyB]: statsB.median },
  ];

  return (
    <Box sx={{ width: "100%", height: 132 }}>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 0.5 }}>
        Столбчатая диаграмма: сравнение среднего и медианы (общая шкала)
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 8, left: 72, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            type="number"
            domain={domain}
            tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={68}
            tick={{ fill: theme.palette.text.primary, fontSize: 12 }}
          />
          <Tooltip
            formatter={(v: number, name: string) => [fmt(v), name]}
            contentStyle={{
              borderRadius: 8,
              border: `1px solid ${theme.palette.divider}`,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar
            name={labelA}
            dataKey={keyA}
            fill={theme.palette.primary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={22}
          />
          <Bar
            name={labelB}
            dataKey={keyB}
            fill={theme.palette.secondary.main}
            radius={[0, 4, 4, 0]}
            maxBarSize={22}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
