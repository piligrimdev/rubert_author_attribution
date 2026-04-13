/** Ответ POST /authors/compute_metrics — плоский объект с полями вида metric_mean, metric_q25, … */
export type AuthorMetricsResponse = Record<string, string | number> & {
  author?: string;
  text_count?: number;
};

export const METRIC_BASE_KEYS = [
  "avg_sent_len_words",
  "avg_word_len_chars",
  "mtld",
  "avg_tree_depth",
  "passive_ratio",
  "func_word_ratio",
  "avg_clauses_per_sent",
  "noun_verb_ratio",
  "compression_ratio",
  "flesch_reading_ease",
  "gunning_fog",
] as const;

export type MetricBaseKey = (typeof METRIC_BASE_KEYS)[number];

export type MetricQuartiles = {
  min: number;
  q25: number;
  median: number;
  q75: number;
  max: number;
  mean: number;
};

export function pickNumber(
  data: AuthorMetricsResponse,
  key: string,
): number | undefined {
  const v = data[key];
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return undefined;
}

export function extractMetricStats(
  data: AuthorMetricsResponse,
  base: MetricBaseKey,
): MetricQuartiles | null {
  const min = pickNumber(data, `${base}_min`);
  const q25 = pickNumber(data, `${base}_q25`);
  const median = pickNumber(data, `${base}_median`);
  const q75 = pickNumber(data, `${base}_q75`);
  const max = pickNumber(data, `${base}_max`);
  const mean = pickNumber(data, `${base}_mean`);
  if (
    min === undefined ||
    q25 === undefined ||
    median === undefined ||
    q75 === undefined ||
    max === undefined ||
    mean === undefined
  ) {
    return null;
  }
  return { min, q25, median, q75, max, mean };
}
