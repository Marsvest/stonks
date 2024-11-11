import asyncio
from tqdm import tqdm

from model import SimModel

# Инициалиация экземпляра модели и даты с парсера
model = SimModel()
data: list[(int, str)] = []


# Асинхронная прослойка
async def save_in_model(price: float, text: str) -> None:
    model.add_embedding(price, text)


# Обучение модели
if __name__ == "__main__":
    for price, text in tqdm(data):
        result = asyncio.run(save_in_model(price, text))
        print(result)
