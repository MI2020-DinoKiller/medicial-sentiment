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
        self.total_all_words = set()
        self.stop_word = set()
        self.dictionaryScore = dict()
        self.command_word = {"COLONCATEGORY", "COMMACATEGORY", "DASHCATEGORY", "ETCCATEGORY", "EXCLAMATIONCATEGORY",
                             "PARENTHESISCATEGORY", "PAUSECATEGORY", "PERIODCATEGORY", "QUESTIONCATEGORY",
                             "SEMICOLONCATEGORY", "SPCHANGECATEGORY"}
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
                sp = line.split(",")
                if len(sp) == 2 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = float(sp[1])
                elif len(sp) == 1 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = 1.0
                else:
                    logging.warning("There is some voc duplicate %s: %d", sp[0], self.dictionaryScore.get(sp[0]))
                self.positive.add(sp[0])
            self.total_all_words = self.total_all_words.union(self.positive)
        logging.info("Read Positive File Success")

        logging.info("Reading Negative File")
        with open(os.path.join(data_path, "negative.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                sp = line.split(",")
                if len(sp) == 2 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = -float(sp[1])
                elif len(sp) == 1 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = -1.0
                else:
                    logging.warning("There is some voc duplicate %s: %d", sp[0], self.dictionaryScore.get(sp[0]))
                self.negative.add(line)
            self.total_all_words = self.total_all_words.union(self.negative)
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
                sp = line.split(",")
                if len(sp) == 2 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = float(sp[1])
                elif len(sp) == 1 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = 1.0
                else:
                    logging.warning("There is some voc duplicate %s: %d", sp[0], self.dictionaryScore.get(sp[0]))
                self.med_positive.add(line)
            self.total_all_words = self.total_all_words.union(self.med_positive)
        logging.info("Read Medicial Positive File Success")

        logging.info("Reading Medicial Negative File")
        with open(os.path.join(data_path, "med_negative.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                sp = line.split(",")
                if len(sp) == 2 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = -float(sp[1])
                elif len(sp) == 1 and self.dictionaryScore.get(sp[0]) is None:
                    self.dictionaryScore[sp[0]] = -1.0
                else:
                    logging.warning("There is some voc duplicate %s: %d", sp[0], self.dictionaryScore.get(sp[0]))
                self.med_negative.add(line)
            self.total_all_words = self.total_all_words.union(self.med_negative)
        logging.info("Read Medicial Negative File Success")

        logging.info("Reading Stop Word File")
        with open(os.path.join(data_path, "stop_word.txt"), "r") as fp:
            for line in fp:
                line = line.strip()
                self.stop_word.add(line)
        logging.info("Read Stop Word File Success")
        self.__loadDic = True
        return

    def toCkipDictionary(self):
        total = set()
        total = total.union(self.med_positive)
        total = total.union(self.med_negative)
        res = dict.fromkeys(total, 1)
        s = construct_dictionary(res)
        return s

    def is_in_total_all_words(self, find_word):
        return find_word in self.total_all_words
