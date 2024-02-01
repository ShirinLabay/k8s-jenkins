import flask
from flask import request
import os
from bot import ObjectDetectionBot
import boto3
import json
import pandas as pd
from telebot.types import InputFile
from deep_translator import GoogleTranslator
from loguru import logger

app = flask.Flask(__name__)
dynamodb_table = 'dynamo-shirin-aws'
secret_name = 'telegram_secrets'
region_name = 'eu-central-1'

# load TELEGRAM_TOKEN value from Secret Manager
secrets_client = boto3.client('secretsmanager', region_name=region_name)
secret_response = secrets_client.get_secret_value(SecretId=secret_name)
secret_data = json.loads(secret_response['SecretString'])
TELEGRAM_TOKEN = secret_data['TELEGRAM_TOKEN']

TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    chat_id = req['message']['chat']['id']
    bot.handle_message(req['message'])
    return 'Ok'


# DynamoDB
# Create a DynamoDB client
dynamodb_client = boto3.client('dynamodb', region_name=region_name)


@app.route(f'/results/', methods=['GET'])
def results():
    prediction_id = request.args.get('predictionId')
    df = pd.read_csv('emoji_df.csv')
    emoji_mapping = dict(zip(df['name'],df['emoji']))

    # Use the prediction_id to retrieve results from DynamoDB
    response = dynamodb_client.get_item(
        TableName='dynamo-shirin-aws',
        Key={
            'prediction_id': {'S': prediction_id}
        }
    )
    if 'Item' in response:
        chat_id = response['Item']['chat_id']['S']
        prediction_summary = response['Item']['prediction_summary']
        predictions_list = prediction_summary['M']['labels']['L']
        detected_objects = {}
        emojis = {}
        for predict_item in predictions_list:
            predict = predict_item['M']
            object_name = predict['class']['S']
            if object_name in detected_objects:
                detected_objects[object_name] += 1
            else:
                detected_objects[object_name] = 1
            label = object_name
            logger.info(object_name)
            matching_names = df[df['name'].str.contains(fr'\b{label}\b', case=False)]['name'].tolist()

            if matching_names:
                # If there are matching names, use the first one
                matching_name = matching_names[0]
                emoji_for_word = emoji_mapping.get(matching_name, '❓')
            else:
                # If there are no matching names, handle the case
                emoji_for_word = '❓'
            emojis[object_name] = emoji_for_word
        text_results = 'Detected objects:\n' + '\n'.join(f'{key}: {value}' for key, value in detected_objects.items())
        text2 = 'The emoji for: ' + '\n'.join(f'{key}: {value}' for key, value in emojis.items())
        bot.send_text(chat_id, text_results)
        bot.send_text(chat_id, text2)
        translated_text = GoogleTranslator(source='auto', target='hebrew').translate(text_results)
        logger.info(f'translated: {translated_text}')
        bot.send_text(chat_id, translated_text)
        return 'Ok'
    else:
        return 'Data not found for the provided predictionId', 404


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)

