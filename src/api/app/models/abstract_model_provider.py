from abc import ABC, abstractmethod


class AbstractModelProvider(ABC):

    @abstractmethod
    async def predict(
            self, text: str, k_nearest: int = 5,
    ) -> list[dict[str, float]]:
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> list:
        pass