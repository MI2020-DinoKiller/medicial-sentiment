import logging
import os
import math

import jieba
import gdown
from ckiptagger import data_utils, WS, POS, NER

from ..dictionary import Dictionary


def word_distance(st, ed, target) -> float:
    if target < st:
        ret = st - target
    elif target > ed:
        ret = target - ed
    else:
        ret = 1
    return float(ret)

class Sent(object):
    def __init__(self, ws, pos, ner):
        self.myDict = Dictionary()
        self.myDict.load()
        self.ws = ws
        self.pos = pos
        self.ner = ner
        self.distance = 10
        return

    """
    judgeSent
    Input:
        sentences = 文章每一段句子
        idf_words = IDF 重要詞
        idf_dict = IDF 重要詞分數
        idf_sum = IDF 重要詞總和分數
    Output:
        score = 總分
        eachScore = 文章每一段句子各個分數
    """

    def judgeSent(self, sentences: [str], idf_words: set, idf_dict: dict, idf_sum: float) -> dict:
        if sentences is None:
            return {"score": 0, "eachScore": [0]}
        """
        1. idf 找出每個段落 sentences 的 idf_words 的位置
        2. 找出每個段落 sentences 的態度詞位置
            1. 找到態度詞後，與所有 idf_words 位置相減取得距離
        """
        idf_in_sentences_location = self.findIDFWordsLocation(sentences, idf_words)
        ret = self.judgeSentences(sentences, idf_dict, idf_in_sentences_location, idf_sum)
        return ret

    def findIDFWordsLocation(self, sentences: [str], idf_words: set):
        ret = []
        for sentence in sentences:
            idf_in_sentence = []
            for counter, char in enumerate(sentence):
                if char in idf_words:
                    idf_in_sentence.append(counter)
            ret.append(idf_in_sentence)
        return ret

    def judgeSentences(self, sentences: [str], idf_dict: dict, idf_in_sentences_location: [list], idf_sum: float):
        score = []
        totalScore = 0.0
        for counter, sentence in enumerate(sentences):
            ret = self.judgeSentence(sentences[counter], idf_dict, idf_in_sentences_location[counter], idf_sum)
            totalScore += ret
            score.append(ret)
        return {"score": totalScore, "eachScore": score}

    def judgeSentence(self, sentence: str, idf_dict: dict, idf_in_sentence_location: [int], idf_sum: float) -> float:
        if sentence is None or idf_in_sentence_location is None:
            return 0.0
        print(sentence)
        print(idf_in_sentence_location)
        start_char_index = 0
        prev_substring = ""
        substring = ""
        prev_res = set()
        score = 0.0
        for counter, char in enumerate(sentence):
            substring += char
            res = set(filter(lambda x: substring in x, self.myDict.total_all_words))
            if res:
                prev_substring = substring
                prev_res = res.copy()
            else:
                substring = ""
                if prev_substring != "" and prev_substring in prev_res:
                    # if self.myDict.is_in_total_all_words(prev_substring):
                    delta = 0.0
                    for i in idf_in_sentence_location:
                        this_word_score = idf_dict[sentence[i]] / idf_sum
                        this_word_score /= word_distance(start_char_index, counter, i)
                        delta += this_word_score
                    delta /= len(idf_in_sentence_location)
                    delta *= self.myDict.dictionaryScore[prev_substring]
                    logging.info("%s, %f", prev_substring, delta)
                    score += delta
                start_char_index = counter + 1
        return score

    # def evaluationComment(self, keywords: list, ws: list, pos: list, negation: bool = False,
    #                       debug: bool = False) -> float:
    #     if len(ws) == 0 or len(keywords) == 0:
    #         return 0.0
    #     n = len(ws)
    #     result = 0.0
    #     keywords = set(keywords)
    #     for i, words in enumerate(ws):
    #         if ws[i] in keywords:
    #             keyWordResult = 0.0
    #             for d in range(-self.distance, self.distance + 1, 1):
    #                 delta = 0.0
    #                 if d != 0 and 0 <= i + d < n and ws[i + d] not in keywords:
    #                     if ws[i + d] in self.myDict.positive:
    #                         delta = 1 / math.pow(d, 2)
    #                     elif ws[i + d] in self.myDict.negative:
    #                         delta = -1 / math.pow(d, 2)
    #                     negationCount = 0
    #                     for j in range(-1, -self.distance, -1):
    #                         if ws[i + d + j] in self.myDict.negation:
    #                             negationCount += 1
    #                         elif pos[i + d + j] in self.myDict.command_word:
    #                             break
    #                     if negationCount % 2 == 1:
    #                         delta = -delta
    #                     keyWordResult += delta
    #                     if debug:
    #                         print(ws[i], ws[i + d], d, delta)
    #             if debug:
    #                 print(keyWordResult)
    #             result += keyWordResult
    #     if negation:
    #         result = -result
    #     # print(ws)
    #     # print(result)
    #     return result

    def evaluationScore(self, keywords: list, wss: list, poss: list, negation: bool = False) -> dict:
        if len(wss) == 0:
            return {"score": 0.0, "eachScore": [0.0]}
        total = 0.0
        scores = []
        for i, sentence in enumerate(wss):
            s = self.evaluationComment(keywords, wss[i], poss[i], negation, debug=True)
            total += s
            scores.append(s)
        return {"score": total / len(wss), "eachScore": scores}

    # def questionToKeyword(self, question: str) -> list:
    #     seg_list = jieba.cut_for_search(question)  # 搜索引擎模式
    #     remainderWords = list(filter(lambda a: a not in self.myDict.stop_word and a != '\n', seg_list))
    #     return remainderWords

    # def taggerQuestion(self, question: str) -> dict:
    #     word_list = self.ws(
    #         [question],
    #         recommend_dictionary=self.myDict.toCkipDictionary(),  # words in this dictionary are encouraged
    #     )
    #
    #     pos_list = self.pos(word_list)
    #     word_list = word_list[0]
    #     pos_list = pos_list[0]
    #     score = 0.0
    #     for w in word_list:
    #         if w in self.myDict.negation:
    #             score -= 1.0
    #
    #     return {"score": score, "ws_result": word_list, "pos_result": pos_list}

    # def tagger(self, sentences: [str]) -> dict:
    #     sentence_list = sentences
    #
    #     word_sentence_list = self.ws(
    #         sentence_list,
    #         recommend_dictionary=self.myDict.toCkipDictionary(),  # words in this dictionary are encouraged
    #     )
    #
    #     pos_sentence_list = self.pos(word_sentence_list)
    #     for i in word_sentence_list:
    #         print(i)
    #     return {"ws": word_sentence_list, "pos": pos_sentence_list}

    def isNegative(self, score: float):
        return score < 0.0

    def isPositive(self, score: float):
        return score > 0.0
