from .abstract_model_provider import AbstractModelProvider

class MockModelProvider(AbstractModelProvider):
    is_embedder = True

    def predict(
            self, text: str, k_nearest: int = 5,
    ) -> list[dict[str, float]]:
        raise NotImplementedError()


    def generate_embedding(self, text: str) -> list:
        return [0]*256