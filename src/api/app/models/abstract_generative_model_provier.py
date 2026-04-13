from abc import ABC, abstractmethod


class AbstractGenerativeModelProvider(ABC):

    @abstractmethod
    async def generate(
            self,
            text: str,
            max_new_tokens: int = 256,
            temperature: float = 0.7,
            top_p: float = 0.9,
            rep_penalty: float = 1.1
    ) -> str:
        raise NotImplementedError()
