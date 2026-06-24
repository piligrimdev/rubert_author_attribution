from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import numpy as np
import structlog
from sklearn.decomposition import PCA

logger = structlog.get_logger(__name__)

RANDOM_STATE = 42

TAB20_HEX = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#aec7e8",
    "#ffbb78",
    "#98df8a",
    "#ff9896",
    "#c5b0d5",
    "#c49c94",
    "#f7b6d2",
    "#c7c7c7",
    "#dbdb8d",
    "#9edae5",
]

TEXT_PREVIEW_LEN = 120


def get_embeddings_for_viz(
    texts: list[dict[str, Any]],
    max_per_author: int = 50,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """
    Берём по max_per_author эмбеддингов от каждого автора.
    Логика совпадает с notebooks/04_bert/finetune_bert_contrasive.ipynb.
    """
    author_indices: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(texts):
        author_indices[str(row["author_id"])].append(i)

    selected_rows: list[dict[str, Any]] = []
    for indices in author_indices.values():
        for idx in indices[:max_per_author]:
            selected_rows.append(texts[idx])

    if not selected_rows:
        raise ValueError("No embeddings selected for visualization")

    matrix = np.stack(
        [np.asarray(row["embedding"], dtype=float) for row in selected_rows]
    )
    return matrix, selected_rows


def reduce_2d(matrix: np.ndarray, method: str = "umap") -> np.ndarray:
    """
    Понижение размерности до 2D: PCA(50) -> UMAP/t-SNE.
    Параметры UMAP совпадают с notebooks/04_bert/.
    """
    n_pca = min(50, matrix.shape[1], matrix.shape[0] - 1)
    if n_pca < 1:
        raise ValueError("Not enough points for dimensionality reduction")

    reduced = PCA(n_components=n_pca, random_state=RANDOM_STATE).fit_transform(matrix)

    if method == "tsne":
        from sklearn.manifold import TSNE

        return TSNE(
            n_components=2,
            perplexity=min(30, len(matrix) // 5),
            random_state=RANDOM_STATE,
            max_iter=1000,
            metric="cosine",
        ).fit_transform(reduced)

    if method == "umap":
        import umap

        n_neighbors = min(15, len(matrix) - 1)
        if n_neighbors < 2:
            raise ValueError("Not enough points for UMAP")

        reducer = umap.UMAP(
            n_components=2,
            n_neighbors=n_neighbors,
            min_dist=0.1,
            metric="cosine",
            random_state=RANDOM_STATE,
        )
        return reducer.fit_transform(reduced)

    raise ValueError(f"Unknown reduction method: {method}")


def _author_color_map(rows: list[dict[str, Any]]) -> dict[str, str]:
    unique_author_ids = sorted({str(row["author_id"]) for row in rows})
    return {
        author_id: TAB20_HEX[i % len(TAB20_HEX)]
        for i, author_id in enumerate(unique_author_ids)
    }


def compute_embedding_compare_umap(
    texts: list[dict[str, Any]],
    *,
    max_per_author: int = 50,
    method: str = "umap",
) -> dict[str, Any]:
    """
    UMAP-проекция эмбеддингов двух авторов для Plotly-графика.
    Возвращает dict в формате EmbeddingUmapResponse.
    """
    logger.info(
        "embedding_umap.processing.started",
        texts_count=len(texts),
        max_per_author=max_per_author,
    )

    matrix, selected_rows = get_embeddings_for_viz(texts, max_per_author)
    coords = reduce_2d(matrix, method=method)
    colors = _author_color_map(selected_rows)

    legend_map: dict[str, dict[str, Any]] = {}
    for row in selected_rows:
        author_id = str(row["author_id"])
        if author_id not in legend_map:
            legend_map[author_id] = {
                "author_id": author_id,
                "author_name": row["author_name"],
                "genre": row.get("genre") or "",
                "source": row.get("source") or "corpus",
                "color": colors[author_id],
            }

    points = []
    for i, row in enumerate(selected_rows):
        author_id = str(row["author_id"])
        text = row.get("text") or ""
        points.append(
            {
                "text_id": row["text_id"],
                "author_id": author_id,
                "author_name": row["author_name"],
                "genre": row.get("genre") or "",
                "source": row.get("source") or "corpus",
                "x": round(float(coords[i, 0]), 4),
                "y": round(float(coords[i, 1]), 4),
                "text_preview": text[:TEXT_PREVIEW_LEN],
                "color": colors[author_id],
            }
        )

    unique_author_ids = sorted({str(row["author_id"]) for row in selected_rows})
    result = {
        "meta": {
            "method": method,
            "n_components": 2,
            "n_points": len(points),
            "n_authors": len(unique_author_ids),
            "color_by": "author",
            "is_mock": False,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "params": {
                "max_per_author": max_per_author,
                "pca_components": min(50, matrix.shape[1], matrix.shape[0] - 1),
                "n_neighbors": min(15, len(matrix) - 1),
                "min_dist": 0.1,
                "metric": "cosine",
            },
        },
        "legend": list(legend_map.values()),
        "points": points,
    }

    logger.info(
        "embedding_umap.processing.finished",
        n_points=len(points),
        n_authors=len(unique_author_ids),
    )
    return result
