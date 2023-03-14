FROM python:3.8-slim

ENV PYTHONPATH=/opt/app
WORKDIR /opt/app

COPY ./requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN mkdir /opt/data
COPY src/ .
COPY ./configs /opt/configs

CMD ["python3", "bot.py"]