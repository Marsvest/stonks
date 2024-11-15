import warnings
import torch
import os
from transformers import BertModel, BertTokenizer
from safetensors.torch import save_file, load_file
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


# Использовать на ТОЛЬКО НА ПРОДЕ (блокирует warning'и)
warnings.filterwarnings("ignore", category=UserWarning)


class SimModel:
    def __init__(self, path_to_model: str = "model.safetensors") -> None:
        model_name = "DeepPavlov/rubert-base-cased"
        self._tokenizer = BertTokenizer.from_pretrained(model_name)
        self._transformer_model = BertModel.from_pretrained(
            model_name
        )  # Use BertModel for embeddings

        self._load_embeddings(path_to_model)

    def _vectorize(self, text: str) -> torch.Tensor:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self._transformer_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings

    def add_embedding(self, price: float, text: str) -> None:
        embedding = self._vectorize(text)
        self.embeddings[str(price)] = embedding

    def save(self, path: str = "model.safetensors") -> None:
        save_file(self.embeddings, path)
        print(f"Model saved to {path}")

    def _load_embeddings(self, path: str) -> None:
        if os.path.exists(path):
            self.embeddings = load_file(path)
            print(f"Model loaded from {path}")
        else:
            self.embeddings = {}
            print("Model created")

    def predict(self, text: str) -> float:
        input_embedding = self._vectorize(text)

        max_similarity = float(-1)
        predict_price = None
        for price, embedding in tqdm(self.embeddings.items()):
            similarity = cosine_similarity(
                input_embedding.numpy().reshape(1, -1), embedding.numpy().reshape(1, -1)
            ).item()
            if similarity > max_similarity:
                max_similarity = similarity
                predict_price = price

        return float(predict_price) if predict_price is not None else 0.0
