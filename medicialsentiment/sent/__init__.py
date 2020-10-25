import logging
import os
import math

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
    # def __init__(self, ws, pos, ner):
    def __init__(self):
        self.myDict = Dictionary()
        self.myDict.load()
        # self.ws = ws
        # self.pos = pos
        # self.ner = ner
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
        each_score = 文章每一段句子各個分數
    """

    def judgeSent(self, sentences: [str], idf_words: set, idf_dict: dict, idf_sum: float) -> dict:
        if sentences is None:
            return {"score": 0, "each_score": [0]}
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
        return {"score": totalScore, "each_score": score}

    def judgeSentence(self, sentence: str, idf_dict: dict, idf_in_sentence_location: [int], idf_sum: float) -> float:
        if sentence is None or idf_in_sentence_location is None:
            return 0.0
        # print(sentence)
        # print(idf_in_sentence_location)
        start_char_index = 0
        prev_substring = ""
        substring = ""
        prev_res = set()
        score = 0.0
        logging.info("Now Sentence is %s:", sentence)
        # for counter, char in enumerate(sentence):
        # for counter in range(len(sentence)):
        counter = 0
        len_limit = len(sentence)
        while counter < len_limit:
            char = sentence[counter]
            substring += char
            res = set(filter(lambda x: substring in x, self.myDict.total_all_words))
            logging.debug("Now Substring %s", substring)
            if res:
                logging.debug("Result %s", res.__str__())
                prev_substring = substring
                prev_res = res.copy()
            else:
                if len(substring) > 1:
                    counter -= 1
                substring = ""
                if prev_substring != "" and prev_substring in prev_res:
                    delta = 0.0
                    for i in idf_in_sentence_location:
                        this_word_score = idf_dict[sentence[i]] / idf_sum
                        this_word_score /= word_distance(start_char_index, counter, i)
                        delta += this_word_score
                    delta /= len(idf_in_sentence_location)
                    delta *= self.myDict.dictionaryScore[prev_substring]
                    logging.info("%s, %f", prev_substring, delta)
                    score += delta
                prev_substring = ""
                prev_res = set()
                start_char_index = counter
            counter += 1
        return score

    def isNegative(self, score: float):
        return score < 0.0

    def isPositive(self, score: float):
        return score > 0.0
