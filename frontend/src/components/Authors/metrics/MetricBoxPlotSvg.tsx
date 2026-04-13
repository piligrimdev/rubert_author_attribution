import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import type { MetricQuartiles } from "@/types/authorMetrics";

type Props = {
  stats: MetricQuartiles;
  /** Подписи min / медиана / max слева */
  formatTick?: (v: number) => string;
};

/**
 * Упрощённый boxplot по агрегатам по текстам (min, q25, медиана, q75, max).
 * Ориентация: вертикальная шкала значений.
 */
export default function MetricBoxPlotSvg({ stats, formatTick }: Props) {
  const theme = useTheme();
  const { min, q25, median, q75, max } = stats;
  const stroke = theme.palette.primary.dark;
  const fill = theme.palette.primary.light;
  const accent = theme.palette.primary.main;

  const lo = Math.min(min, q25, median, q75, max);
  const hi = Math.max(min, q25, median, q75, max);
  const span = hi - lo || 1;

  const W = 140;
  const H = 160;
  const padT = 12;
  const padB = 28;
  const cx = W / 2;
  const plotH = H - padT - padB;

  const y = (v: number) => padT + ((hi - v) / span) * plotH;

  const yMin = y(min);
  const yQ1 = y(q25);
  const yMed = y(median);
  const yQ3 = y(q75);
  const yMax = y(max);

  const boxTop = Math.min(yQ1, yQ3);
  const boxH = Math.abs(yQ3 - yQ1) || 1;

  const fmt = formatTick ?? ((v: number) => v.toFixed(2));

  return (
    <Box sx={{ display: "flex", gap: 1, alignItems: "stretch" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          py: `${padT}px`,
          pb: `${padB}px`,
          minWidth: 44,
        }}
      >
        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.1 }}>
          {fmt(hi)}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.1 }}>
          {fmt(lo)}
        </Typography>
      </Box>
      <svg
        width="100%"
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="xMidYMid meet"
        aria-hidden
      >
        {/* нижний ус */}
        <line
          x1={cx}
          y1={yMin}
          x2={cx}
          y2={boxTop + boxH}
          stroke={stroke}
          strokeWidth={1.5}
        />
        {/* верхний ус */}
        <line
          x1={cx}
          y1={boxTop}
          x2={cx}
          y2={yMax}
          stroke={stroke}
          strokeWidth={1.5}
        />
        {/* капы */}
        <line
          x1={cx - 18}
          y1={yMin}
          x2={cx + 18}
          y2={yMin}
          stroke={stroke}
          strokeWidth={1.5}
        />
        <line
          x1={cx - 18}
          y1={yMax}
          x2={cx + 18}
          y2={yMax}
          stroke={stroke}
          strokeWidth={1.5}
        />
        {/* ящик */}
        <rect
          x={cx - 22}
          y={boxTop}
          width={44}
          height={boxH}
          fill={fill}
          fillOpacity={0.35}
          stroke={stroke}
          strokeWidth={1.5}
        />
        {/* медиана */}
        <line
          x1={cx - 22}
          y1={yMed}
          x2={cx + 22}
          y2={yMed}
          stroke={accent}
          strokeWidth={2.5}
        />
      </svg>
    </Box>
  );
}
