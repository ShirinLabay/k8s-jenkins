FROM python:3.14.0a1-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
CMD [ "python3", "app.py" ]