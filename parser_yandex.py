import feedparser
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

# URL RSS-ленты
rss_url = "https://ria.ru/export/rss2/archive/index.xml"

# Установим временные границы
moscow_tz = pytz.timezone("Europe/Moscow")
start_time_msk = moscow_tz.localize(datetime(2024, 10, 14))  # 00:00 MSK
utc_tz = pytz.UTC
start_time_utc = start_time_msk.astimezone(utc_tz)  # Переводим в UTC для фильтрации

# Парсинг RSS-ленты
feed = feedparser.parse(rss_url)

# Открываем файл для записи новостей
with open("ria_news_content_only.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)

    # Обход по всем новостям в ленте
    for entry in tqdm(feed.entries):
        # Преобразование даты публикации в объект datetime
        pub_date_utc = datetime(
            *entry.published_parsed[:6]
        )  # Предполагаем, что это UTC
        if pub_date_utc.tzinfo is None:  # Проверка на наличие временной зоны
            pub_date_utc = pub_date_utc.replace(tzinfo=pytz.UTC)
        pub_date_msk = pub_date_utc.astimezone(moscow_tz)  # Переводим в MSK

        # Фильтрация новостей по дате и времени (используем UTC для фильтрации)
        if pub_date_utc >= start_time_utc:
            # Переход по ссылке для извлечения текста новости
            try:
                article_response = requests.get(entry.link)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, "html.parser")

                # Сбор текста из всех блоков `article__block`, содержащих `article__text`
                content_parts = []
                for block in article_soup.find_all("div", class_="article__block"):
                    text_block = block.find("div", class_="article__text")
                    if text_block:
                        content_parts.append(text_block.get_text(strip=True))

                # Объединение всех частей текста
                content = (
                    "\n".join(content_parts)
                    if content_parts
                    else "Текст новости не найден"
                )

                # Запись в CSV файл с MSK датой и текстом новости
                csv_writer.writerow(
                    [pub_date_msk.timestamp(), content]
                )

            except Exception as e:
                print(f"Ошибка при получении текста новости: {e}")

print("Сбор новостей завершен.")
