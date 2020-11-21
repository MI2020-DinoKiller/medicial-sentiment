import os
import sys
import json
import time
import logging
import pika
from medicialsentiment.sent import Sent
from medicialsentiment.copeopi import CopeOpi
from ckiptagger import data_utils, WS, POS, NER

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename='myLog.log', filemode='w', format=FORMAT)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logging.info("Loading config.json......")
dataPath = os.path.dirname(os.path.abspath(__file__))
input_file = open(os.path.join(dataPath, 'config.json'))
CONFIG = json.load(input_file)
logging.info("Load config.json Success!")

logging.info("Loading CKIP Package......")
if not os.path.exists('./data'):
    logging.info("Downloading CKIP Data......")
    data_utils.download_data_gdown("./")  # gdrive-ckip
    logging.info("Download CKIP Data Success")
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")
logging.info("Load CKIP Package Success!")

sent = Sent()
copeopi = CopeOpi(ws, pos, ner)

logging.info('[*] Connecting RabbitMQ......')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=CONFIG["RABBITMQ"]["HOST"]))
channel = connection.channel()
logging.info('[*] Connecting RabbitMQ Success!')
channel.queue_declare(queue=CONFIG["RABBITMQ"]["QUEUENAME"], durable=True)
logging.info('[*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    body = body.decode("utf-8")
    obj = json.loads(body)
    logging.info("[x] Received " + str(obj))
    time_start = time.time()
    query_string = obj["query_string"]
    sentences = obj["sentence"]
    idf_dict = obj["idf_dict"]
    idf_words = set(obj["idf_words"])
    idf_sum = float(obj["idf_sum"])
    ret = sent.judge_sent(query_string=query_string, sentences=sentences, idf_words=idf_words,
                          idf_dict=idf_dict, idf_sum=idf_sum)
    # if sentences is not None:
    #     print(ret["score"])
    #     print(obj["url"])
    #     for counter, sentence in enumerate(sentences):
    #         print(ret["each_score"][counter], ":", sentence)
    #     print()
    #     print("=" * 10)
    #     print()
    ret2 = copeopi.getOpinionScore(obj)
    if sentences is not None:
        print(ret["score"], ret2["score"])
        print(obj["url"])
        for counter, sentence in enumerate(sentences):
            print(ret["each_score"][counter], ret2["each_score"][counter], ":", sentence)
        print()
        print("=" * 10)
        print()
    # print(ret2["score"])
    # print(ret2["each_score"])
    # if (ret["score"] < 0 < ret2["score"]) or (ret["score"] > 0 > ret2["score"]):
    #     for i, element in enumerate(obj["sentence"]):
    #         print(element)
    #         print(ret["each_score"][i], ret2["each_score"][i])
    # time_end = time.time()
    # logging.info('[*] time cost ' + str(time_end - time_start) + 's')
    # logging.info("[*] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(CONFIG["RABBITMQ"]["QUEUENAME"], callback)
channel.start_consuming()
