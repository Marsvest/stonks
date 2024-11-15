import feedparser
import pandas as pd
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

# URL RSS-ленты
rss_url = 'https://ria.ru/export/rss2/archive/index.xml'

# Московская временная зона
moscow_tz = pytz.timezone('Europe/Moscow')
start_time = moscow_tz.localize(datetime(2024, 11, 15, 0, 0))  # Время начала сбора с 15 ноября 2024, 00:00

# Парсинг RSS-ленты
feed = feedparser.parse(rss_url)

# Список для хранения новостей
news_list = []

# Обход по всем новостям в ленте
for entry in feed.entries:
    # Преобразование даты публикации в объект datetime и перевод в московское время
    pub_date_utc = datetime(*entry.published_parsed[:6])
    if pub_date_utc.tzinfo is None:  # Проверка на наличие временной зоны
        pub_date_utc = pub_date_utc.replace(tzinfo=pytz.UTC)
    pub_date_moscow = pub_date_utc.astimezone(moscow_tz)

    # Фильтрация новостей по дате и времени
    if pub_date_moscow >= start_time:
        # Переход по ссылке для извлечения текста новости
        try:
            article_response = requests.get(entry.link)
            article_response.raise_for_status()
            article_soup = BeautifulSoup(article_response.text, 'html.parser')

            # Сбор текста из всех блоков `article__block`, содержащих `article__text`
            content_parts = []
            for block in article_soup.find_all('div', class_='article__block'):
                text_block = block.find('div', class_='article__text')
                if text_block:
                    content_parts.append(text_block.get_text(strip=True))

            # Объединение всех частей текста
            content = "\n".join(content_parts) if content_parts else "Текст новости не найден"

        except Exception as e:
            content = f"Ошибка при получении текста новости: {e}"

        # Добавляем в список новостей только дату и текст новости
        news_list.append({
            'Дата и время': pub_date_moscow.strftime("%Y-%m-%d %H:%M:%S"),
            'Текст новости': content
        })

# Создание DataFrame
df = pd.DataFrame(news_list)

# Сортировка по дате и времени
df_sorted = df.sort_values(by='Дата и время', ascending=True)

# Сохранение в CSV без заголовков
df_sorted.to_csv('ria_news_content_only2.csv', index=False, encoding='utf-8', header=False)

print("Сбор и сортировка новостей завершены.")
