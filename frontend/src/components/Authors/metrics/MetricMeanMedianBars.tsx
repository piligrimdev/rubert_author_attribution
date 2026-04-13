import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
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
import type { MetricQuartiles } from "@/types/authorMetrics";

type Props = {
  stats: MetricQuartiles;
  formatValue?: (v: number) => string;
};

/** Два столбца: среднее и медиана по текстам автора; общая шкала в диапазоне min–max. */
export default function MetricMeanMedianBars({ stats, formatValue }: Props) {
  const theme = useTheme();
  const fmt = formatValue ?? ((v: number) => String(v));
  const { min, max, mean, median } = stats;
  const lo = Math.min(min, mean, median);
  const hi = Math.max(max, mean, median);
  const pad = (hi - lo) * 0.08 || 0.01;
  const domain: [number, number] = [lo - pad, hi + pad];

  const data = [
    { name: "Среднее", value: mean },
    { name: "Медиана", value: median },
  ];

  return (
    <Box sx={{ width: "100%", height: 112 }}>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 0.5 }}>
        Столбчатая диаграмма: среднее и медиана (та же шкала, что и у ящика)
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
            formatter={(v: number) => [fmt(v), ""]}
            contentStyle={{
              borderRadius: 8,
              border: `1px solid ${theme.palette.divider}`,
            }}
          />
          <Bar
            dataKey="value"
            radius={[0, 6, 6, 0]}
            fill={theme.palette.primary.main}
            maxBarSize={28}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
