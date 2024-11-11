import asyncio
from tqdm import tqdm

from model import SimModel

# Инициалиация экземпляра модели и даты с парсера
model = SimModel()
data = [("example", "example"), ("test for text", "test for seq")]


# Асинхронная прослойка
async def predict(text1, text2) -> float:
    return model.get_similarity(text1, text2)


if __name__ == "__main__":
    for text1, text2 in tqdm(data):
        result = asyncio.run(predict(text1, text2))
        print(result)
