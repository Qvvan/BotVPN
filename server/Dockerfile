FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Убедимся, что мы в правильной папке
WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Изменяем порт на 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "12345", "--reload"]

# Настраиваем expose на новый порт
EXPOSE 12345
