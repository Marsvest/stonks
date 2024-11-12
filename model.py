import torch
import os
from transformers import AutoTokenizer, AutoModel
from safetensors.torch import save_file, load_file
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


# KEY: Percent increase or decrease of stock function after this news items
# VALUE: Tensor of news items linked to this price
class SimModel:
    def __init__(self, path_to_model: str = "model.safetensors") -> None:
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._transformer_model = AutoModel.from_pretrained(model_name)

        self._load_embeddings(path_to_model)

    def _vectorize(self, text: str) -> torch.Tensor:
        inputs = self._tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
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
        for price, embedding in tqdm(self.embeddings.items()):
            similarity = cosine_similarity(input_embedding, embedding).item()
            if similarity > max_similarity:
                max_similarity = similarity
                predict_price = price

        return float(predict_price)
