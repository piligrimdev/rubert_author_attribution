export type EmbeddingUmapColorBy = "author" | "genre" | "source";

export type EmbeddingUmapParams = {
  max_per_author: number;
  pca_components: number;
  n_neighbors: number;
  min_dist: number;
  metric: string;
};

export type EmbeddingUmapMeta = {
  method: "umap" | "tsne";
  n_components: number;
  n_points: number;
  n_authors: number;
  color_by: EmbeddingUmapColorBy;
  is_mock: boolean;
  computed_at: string;
  params: EmbeddingUmapParams;
};

export type EmbeddingUmapAuthorLegendItem = {
  author_id: string;
  author_name: string;
  genre: string;
  source: string;
  color: string;
};

export type EmbeddingUmapPoint = {
  text_id: string;
  author_id: string;
  author_name: string;
  genre: string;
  source: string;
  x: number;
  y: number;
  text_preview: string;
  color: string;
};

export type EmbeddingUmapResponse = {
  meta: EmbeddingUmapMeta;
  legend: EmbeddingUmapAuthorLegendItem[];
  points: EmbeddingUmapPoint[];
};
