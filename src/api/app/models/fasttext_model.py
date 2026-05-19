#import fasttext
from .abstract_model_provider import AbstractModelProvider

class FasttextModelProvider(AbstractModelProvider):
    is_embedder = False

    def __init__(self, path_to_pretrained_model: str):
        #self.model = fasttext.load_model(path_to_pretrained_model)
        self.model = None

    def predict(self, text: str, k_nearest = 5) -> list:
        return self.model.predict(text, k=k_nearest)

    def generate_embedding(self, text: str) -> list:
        return self.model.get_sentence_vector(text)

