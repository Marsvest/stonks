from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity


class SimModel:
    # Загрузка предобученной модели и токенизатора
    def __init__(self) -> None:
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModel.from_pretrained(model_name)

    def _get_embedding(self, text: str) -> torch.Tensor:
        # Токенизация и подготовка тензоров
        inputs = self._tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self._model(**inputs)
        # Извлечение эмбеддинга, усредняя скрытые состояния для токенов
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings

    def get_similarity(self, text1: str, text2: str) -> float:
        # Получение эмбеддингов
        embedding1 = self._get_embedding(text1)
        embedding2 = self._get_embedding(text2)

        # Расчет косинусного сходства
        similarity = cosine_similarity(embedding1, embedding2).item()
        return similarity
