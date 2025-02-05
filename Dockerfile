FROM python:3.12
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]