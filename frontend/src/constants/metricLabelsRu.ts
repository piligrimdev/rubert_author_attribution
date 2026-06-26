import type { MetricBaseKey } from "@/types/authorMetrics";
import { METRIC_BASE_KEYS } from "@/types/authorMetrics";
import { strings } from "@/i18n/strings";

export type MetricRuMeta = {
  key: MetricBaseKey;
  title: string;
  description: string;
  unitHint: string;
};

export const METRIC_RU = Object.fromEntries(
  METRIC_BASE_KEYS.map((key) => [
    key,
    { key, ...strings.metrics.items[key] },
  ]),
) as Record<MetricBaseKey, MetricRuMeta>;
