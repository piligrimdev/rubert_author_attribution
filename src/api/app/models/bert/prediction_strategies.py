from numpy import mean
from collections import Counter, defaultdict

from ...schemas.responses import NearestTextItem, VotesResponse

def votes_with_sim_threshold(
    nearest_embeddings: list[NearestTextItem],
    threshold: float = 0.5
) -> VotesResponse:
    """
    считает эмбеддинг, смотрит ближайших соседей, выбирает самого часто встречающегося автора
    """

    votes = Counter(n.author_id for n in nearest_embeddings)
    avg_sim = mean([n.distance for n in nearest_embeddings])
    top_sim = 1 - (nearest_embeddings[0].distance if nearest_embeddings else 0)

    predicted = votes.most_common(1)[0][0]

    # если самый ближайший слишком далеко - не понятно, кто это
    if top_sim < threshold:
        predicted = None

    return VotesResponse(
        predicted=predicted,
        confidence=top_sim,
        avg_sim=avg_sim,
        votes={str(k): v for k, v in votes.items()},
        items=nearest_embeddings,
    )