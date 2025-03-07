
FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./.env /code/.env

COPY ./app /code/app

#EXPOSE 8000

CMD ["python", "-m", "app.run"]


