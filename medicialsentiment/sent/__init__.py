import logging
import os
import math

import jieba
import gdown
from ckiptagger import data_utils, WS, POS, NER

from ..dictionary import Dictionary


class Sent(object):
    def __init__(self, ws, pos, ner):
        self.myDict = Dictionary()
        self.myDict.load()
        self.ws = ws
        self.pos = pos
        self.ner = ner
        jieba.load_userdict(os.path.join(self.myDict.data_path, "med_positive.txt"))
        jieba.load_userdict(os.path.join(self.myDict.data_path, "med_negative.txt"))
        self.distance = 10
        return

    def judgeSent(self, question: str, sentences: [str]) -> dict:
        s = self.taggerQuestion(question)
        remainderWords = self.questionToKeyword(question)
        t = self.tagger(sentences)
        print(t["ws"])
        print(remainderWords)
        result = self.evaluationScore(remainderWords, t["ws"], t["pos"], s["score"] < 0.0)
        return result

    def evaluationComment(self, keywords: list, ws: list, pos: list, negation: bool = False,
                          debug: bool = False) -> float:
        if len(ws) == 0 or len(keywords) == 0:
            return 0.0
        n = len(ws)
        result = 0.0
        keywords = set(keywords)
        for i, words in enumerate(ws):
            if ws[i] in keywords:
                for d in range(-self.distance, self.distance + 1, 1):
                    delta = 0.0
                    if d < 0 and 0 <= i + d < n and ws[i + d] not in keywords:
                        if ws[i + d] in self.myDict.positive:
                            delta = min(1 / math.pow(d, 2), 0.05)
                        elif ws[i + d] in self.myDict.med_positive:
                            delta = min(0.5 / math.pow(d, 2), 0.05)
                        elif ws[i + d] in self.myDict.negation:
                            if d < -1:
                                d += 1
                                delta = max(-1 / math.pow(d, 2), -0.05)
                            else:
                                delta = max(-1 / math.pow(d, 2), -0.05)
                                d += 1
                        elif ws[i + d] in self.myDict.negative:
                            delta = max(-1 / math.pow(d, 2), -0.05)
                        elif ws[i + d] in self.myDict.med_negative:
                            delta = max(-0.5 / math.pow(d, 2), -0.05)
                    elif d != 0 and 0 <= i + d < n and ws[i + d] not in keywords:
                        delta = 0.0
                        if ws[i + d] in self.myDict.positive:
                            delta = 1 / math.pow(d, 2)
                        elif ws[i + d] in self.myDict.med_positive:
                            delta = 0.5 / math.pow(d, 2)
                        elif ws[i + d] in self.myDict.negation:
                            if d < -1:
                                d += 1
                                delta = -1 / math.pow(d, 2)
                            else:
                                delta = -1 / math.pow(d, 2)
                                d += 1
                        elif ws[i + d] in self.myDict.negative:
                            delta = -1 / math.pow(d, 2)
                        elif ws[i + d] in self.myDict.med_negative:
                            delta = -0.5 / math.pow(d, 2)
                    result += delta
                    if debug and delta != 0.0:
                        print(ws[i], ws[i + d], d, delta)
        if negation:
            result = -result
        # print(ws)
        # print(result)
        return result

    def evaluationScore(self, keywords: list, wss: list, poss: list, negation: bool = False) -> dict:
        if len(wss) == 0:
            return {"score": 0.0, "eachScore": [0.0]}
        total = 0.0
        scores = []
        for i, sentence in enumerate(wss):
            s = self.evaluationComment(keywords, wss[i], poss[i], negation)
            total += s
            scores.append(s)
        return {"score": total / len(wss), "eachScore": scores}

    def questionToKeyword(self, question: str) -> list:
        seg_list = jieba.cut_for_search(question)  # 搜索引擎模式
        remainderWords = list(filter(lambda a: a not in self.myDict.stop_word and a != '\n', seg_list))
        return remainderWords

    def taggerQuestion(self, question: str) -> dict:
        word_list = self.ws(
            [question],
            recommend_dictionary=self.myDict.toCkipDictionary(),  # words in this dictionary are encouraged
        )

        pos_list = self.pos(word_list)
        word_list = word_list[0]
        pos_list = pos_list[0]
        score = 0.0
        for w in word_list:
            if w in self.myDict.negation:
                score -= 1.0

        return {"score": score, "ws_result": word_list, "pos_result": pos_list}

    def tagger(self, sentences: [str]) -> dict:
        sentence_list = sentences

        word_sentence_list = self.ws(
            sentence_list,
            recommend_dictionary=self.myDict.toCkipDictionary(),  # words in this dictionary are encouraged
        )

        pos_sentence_list = self.pos(word_sentence_list)
        # for i in word_sentence_list:
        #     print(i)
        return {"ws": word_sentence_list, "pos": pos_sentence_list}

    def isNegative(self, score: float):
        return score < 0.0

    def isPositive(self, score: float):
        return score > 0.0
