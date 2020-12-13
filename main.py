import os
import sys
import json
import time
import logging
import pika
from medicialsentiment.sent import Sent
from medicialsentiment.copeopi import CopeOpi
from medicialsentiment.sqlconnect import SQLConnect
from ckiptagger import data_utils, WS, POS, NER
from medicialsentiment.utils import content_cut_from_sentence

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename='myLog.log', filemode='w', format=FORMAT)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logging.info("Loading config.json......")
dataPath = os.path.dirname(os.path.abspath(__file__))
input_file = open(os.path.join(dataPath, 'config.json'))
CONFIG = json.load(input_file)
logging.info("Load config.json Success!")

# logging.info("Loading CKIP Package......")
# if not os.path.exists('./data'):
#     logging.info("Downloading CKIP Data......")
#     data_utils.download_data_gdown("./")  # gdrive-ckip
#     logging.info("Download CKIP Data Success")
# ws = WS("./data")
# pos = POS("./data")
# ner = NER("./data")
# logging.info("Load CKIP Package Success!")

sent = Sent()
# copeopi = CopeOpi(ws, pos, ner)

logging.info('[*] Connecting Database......')
database = SQLConnect(host=CONFIG["DATABASE"]["HOST"],
                      username=CONFIG["DATABASE"]["USERNAME"],
                      password=CONFIG["DATABASE"]["PASSWORD"],
                      db_name=CONFIG["DATABASE"]["DB_NAME"],
                      charset=CONFIG["DATABASE"]["CHARSET"])
database.connect()
logging.info('[*] Connecting Database Success!')

logging.info('[*] Connecting RabbitMQ......')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=CONFIG["RABBITMQ"]["HOST"], heartbeat=0,))
channel = connection.channel()
logging.info('[*] Connecting RabbitMQ Success!')
channel.queue_declare(queue=CONFIG["RABBITMQ"]["QUEUENAME"], durable=True)
logging.info('[*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    body = body.decode("utf-8")
    obj = json.loads(body)
    logging.debug("[x] Received " + str(obj))
    query_string = obj["query_string"]
    sentences = obj["sentence"]
    idf_dict = obj["idf_dict"]
    idf_words = set(obj["idf_words"])
    idf_sum = float(obj["idf_sum"])
    content = obj["content"]
    ret = sent.judge_sent(query_string=query_string, sentences=sentences, idf_words=idf_words,
                          idf_dict=idf_dict, idf_sum=idf_sum)
    if sentences is not None and sentences != []:
        print(ret["score"])
        print(obj["url"])
        for counter, sentence in enumerate(sentences):
            print(ret["each_score"][counter], ":", sentence)
        print()
        print("=" * 10)
        print()
        obj["sentence"], ret["each_score"] = content_cut_from_sentence(content, obj["sentence"], ret["each_score"])
        print(content)
        for counter, sentence in enumerate(obj["sentence"]):
            print(ret["each_score"][counter], ":", sentence)
        database.insert_search_result_score(obj['search_id'], obj["url"], obj["title"],
                                            ret["score"], obj["sentence"], ret["each_score"])

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(CONFIG["RABBITMQ"]["QUEUENAME"], callback)
channel.start_consuming()
