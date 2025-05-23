# Відповідає тому, що лежить у корені: d.toml, src/, apps/, settings/, .env тощо
FROM python:3.13-slim

# 1. Встановлюємо Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# 2. Копіюємо файли з залежностями
COPY pyproject.toml poetry.lock* /app/

# 3. Встановлюємо залежності без створення віртуального оточення
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "src.api.v1.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]