import os
import logging
from ckiptagger import construct_dictionary

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))


class Dictionary(object):
    def __init__(self):
        self.data_path = os.path.dirname(os.path.abspath(__file__))
        self.__loadDic = False
        self.positive = set()
        self.negative = set()
        self.negation = set()
        self.med_positive = set()
        self.med_negative = set()
        self.stop_word = set()
        return

    def load(self):
        if self.__loadDic:
            logging.info("Dictionary has been loaded.")
            return
        logging.info("Dictionary loading...")

        logging.info("Reading Positive File")
        with open(os.path.join(data_path, "positive.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.positive.add(line)
        logging.info("Read Positive File Success")

        logging.info("Reading Negative File")
        with open(os.path.join(data_path, "negative.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.negative.add(line)
        logging.info("Read Negative File Success")

        logging.info("Reading Negation File")
        with open(os.path.join(data_path, "negation.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.negation.add(line)
        logging.info("Read Negation File Success")

        logging.info("Reading Medicial Positive File")
        with open(os.path.join(data_path, "med_positive.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.med_positive.add(line)
        logging.info("Read Medicial Positive File Success")

        logging.info("Reading Medicial Negative File")
        with open(os.path.join(data_path, "med_negative.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.med_negative.add(line)
        logging.info("Read Medicial Negative File Success")

        logging.info("Reading Stop Word File")
        with open(os.path.join(data_path, "stop_word.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.stop_word.add(line)
        logging.info("Read Stop Word File Success")
        return


    def toCkipDictionary(self):
        total = set()
        total = total.union(self.med_positive)
        total = total.union(self.med_negative)
        res = dict.fromkeys(total, 1)
        s = construct_dictionary(res)
        return s
