FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "wiki.wsgi:application"]