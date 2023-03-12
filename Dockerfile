FROM python:3.8-slim

ENV PYTHONPATH=/opt/app
WORKDIR /opt/app

RUN pip install  --default-timeout=1000 --prefer-binary --no-cache-dir -r /requirements.txt && mkdir /opt/data
COPY src/ .

CMD ["python3", "bot.py"]