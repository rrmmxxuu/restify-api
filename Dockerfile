FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY . .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
