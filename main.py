import asyncio
from tqdm import tqdm

from model import SimModel

# Инициалиация экземпляра модели и даты с парсера
model = SimModel()
data: list[(float, str)] = []


# Асинхронная прослойка
async def add_to_model(price: float, text: str) -> None:
    model.add_embedding(price, text)


# Обучение модели
def train() -> None:
    for price, text in tqdm(data):
        asyncio.run(add_to_model(price, text))

    model.save()


if __name__ == "__main__":
    print(
        model.predict(
            "Компания объявила о значительном сокращении затрат и увеличении годового прогноза прибыли."
        )
    )
