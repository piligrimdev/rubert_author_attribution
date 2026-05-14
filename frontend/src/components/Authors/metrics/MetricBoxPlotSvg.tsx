import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import type { MetricQuartiles } from "@/types/authorMetrics";

type Props = {
  stats: MetricQuartiles;
  /** Подписи шкалы слева (верх/низ диапазона) */
  formatTick?: (v: number) => string;
  /** Цвета: второй автор в режиме сравнения */
  colorVariant?: "primary" | "secondary";
};

/**
 * Упрощённый boxplot по агрегатам по текстам (min, q25, медиана, q75, max) + среднее.
 * На графике подписаны квартили, медиана, среднее и крайние значения.
 */
export default function MetricBoxPlotSvg({
  stats,
  formatTick,
  colorVariant = "primary",
}: Props) {
  const theme = useTheme();
  const palette =
    colorVariant === "secondary" ? theme.palette.secondary : theme.palette.primary;
  const { min, q25, median, q75, max, mean } = stats;
  const stroke = palette.dark;
  const fill = palette.light;
  const accent = palette.main;
  const meanStroke = theme.palette.warning.main;

  const lo = Math.min(min, q25, median, q75, max, mean);
  const hi = Math.max(min, q25, median, q75, max, mean);
  const span = hi - lo || 1;

  const W = 200;
  const H = 178;
  const padT = 12;
  const padB = 10;
  const cx = 78;
  const plotH = H - padT - padB;
  const labelX = cx + 30;

  const yAt = (v: number) => padT + ((hi - v) / span) * plotH;

  const yMin = yAt(min);
  const yQ1 = yAt(q25);
  const yMed = yAt(median);
  const yQ3 = yAt(q75);
  const yMax = yAt(max);
  const yMean = yAt(mean);

  const boxTop = Math.min(yQ1, yQ3);
  const boxH = Math.abs(yQ3 - yQ1) || 1;

  const fmt = formatTick ?? ((v: number) => v.toFixed(2));

  type Lbl = { y: number; text: string; key: string };
  const labelCandidates: Lbl[] = [
    { y: yMax, text: `макс ${fmt(max)}`, key: "max" },
    { y: yQ3, text: `Q3 ${fmt(q75)}`, key: "q3" },
    { y: yMed, text: `мед ${fmt(median)}`, key: "med" },
    { y: yMean, text: `сред ${fmt(mean)}`, key: "mean" },
    { y: yQ1, text: `Q1 ${fmt(q25)}`, key: "q1" },
    { y: yMin, text: `мин ${fmt(min)}`, key: "min" },
  ];
  labelCandidates.sort((a, b) => a.y - b.y);
  const minGap = 12;
  let prevY = -1e9;
  const labels: Lbl[] = labelCandidates.map((row) => {
    let yy = row.y;
    if (yy - prevY < minGap) yy = prevY + minGap;
    prevY = yy;
    return { ...row, y: yy };
  });

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
        {/* среднее — пунктир через ящик */}
        <line
          x1={cx - 22}
          y1={yMean}
          x2={cx + 22}
          y2={yMean}
          stroke={meanStroke}
          strokeWidth={2}
          strokeDasharray="5 4"
        />
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
        {labels.map((row, i) => (
          <text
            key={row.key}
            x={labelX + (i % 2) * 34}
            y={row.y}
            fill={theme.palette.text.secondary}
            fontSize={9}
            dominantBaseline="middle"
          >
            {row.text}
          </text>
        ))}
      </svg>
    </Box>
  );
}
