FROM python:3.13.0a4-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
CMD [ "python3", "app.py" ]