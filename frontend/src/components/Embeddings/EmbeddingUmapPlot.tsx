import { useMemo } from "react";
import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import type { Data, Layout, Config } from "plotly.js";
import Box from "@mui/material/Box";
import type { EmbeddingUmapResponse } from "@/types/embeddingUmap";

const Plot = createPlotlyComponent(Plotly);

type Props = {
  data: EmbeddingUmapResponse;
  height?: number;
};

function groupPointsByAuthor(data: EmbeddingUmapResponse) {
  const byAuthor = new Map<
    string,
    { name: string; color: string; xs: number[]; ys: number[]; previews: string[]; genres: string[]; sources: string[] }
  >();

  for (const point of data.points) {
    const key = point.author_id;
    const bucket = byAuthor.get(key) ?? {
      name: point.author_name,
      color: point.color,
      xs: [],
      ys: [],
      previews: [],
      genres: [],
      sources: [],
    };
    bucket.xs.push(point.x);
    bucket.ys.push(point.y);
    bucket.previews.push(point.text_preview);
    bucket.genres.push(point.genre);
    bucket.sources.push(point.source);
    byAuthor.set(key, bucket);
  }

  return [...byAuthor.values()];
}

export default function EmbeddingUmapPlot({ data, height = 560 }: Props) {
  const traces = useMemo<Data[]>(() => {
    return groupPointsByAuthor(data).map((group) => ({
      type: "scattergl",
      mode: "markers",
      name: group.name,
      x: group.xs,
      y: group.ys,
      marker: {
        color: group.color,
        size: 7,
        opacity: 0.75,
        line: { width: 0 },
      },
      text: group.previews.map(
        (preview, i) =>
          `<b>${group.name}</b><br>` +
          `Жанр: ${group.genres[i]}<br>` +
          `Источник: ${group.sources[i]}<br>` +
          `${preview}`,
      ),
      hoverinfo: "text",
    }));
  }, [data]);

  const layout = useMemo<Partial<Layout>>(
    () => ({
      title: {
        text: `UMAP-проекция эмбеддингов (${data.meta.n_points} точек, ${data.meta.n_authors} авторов)`,
        font: { family: "'Playfair Display', serif", size: 18, color: "#3E2723" },
      },
      paper_bgcolor: "#FFFBF5",
      plot_bgcolor: "#F5F0EB",
      font: { family: "'Inter', sans-serif", color: "#3E2723" },
      xaxis: {
        title: "UMAP-1",
        gridcolor: "rgba(109, 76, 65, 0.15)",
        zerolinecolor: "rgba(109, 76, 65, 0.2)",
      },
      yaxis: {
        title: "UMAP-2",
        gridcolor: "rgba(109, 76, 65, 0.15)",
        zerolinecolor: "rgba(109, 76, 65, 0.2)",
      },
      legend: {
        orientation: "v",
        x: 1.02,
        y: 1,
        font: { size: 11 },
        bgcolor: "rgba(255, 251, 245, 0.9)",
        bordercolor: "rgba(109, 76, 65, 0.2)",
        borderwidth: 1,
      },
      margin: { l: 48, r: 180, t: 64, b: 48 },
      hovermode: "closest",
      dragmode: "zoom",
    }),
    [data.meta.n_authors, data.meta.n_points],
  );

  const config = useMemo<Partial<Config>>(
    () => ({
      responsive: true,
      displayModeBar: true,
      scrollZoom: true,
      modeBarButtonsToRemove: ["select2d", "lasso2d"],
    }),
    [],
  );

  return (
    <Box sx={{ width: "100%", minHeight: height }}>
      <Plot
        data={traces}
        layout={layout}
        config={config}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler
      />
    </Box>
  );
}
