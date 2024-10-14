FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ../app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

EXPOSE 80