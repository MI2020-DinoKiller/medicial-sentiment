import logging

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
        self.except_med_words = set()
        # self.ws = ws
        # self.pos = pos
        # self.ner = ner
        # self.distance = 10
        return

    """
    judge_sent
    Input:
        sentences = 文章每一段句子
        idf_words = IDF 重要詞
        idf_dict = IDF 重要詞分數
        idf_sum = IDF 重要詞總和分數
    Output:
        score = 總分
        each_score = 文章每一段句子各個分數
    """

    def judge_sent(self, query_string: str, sentences: [str], idf_words: set, idf_dict: dict, idf_sum: float) -> dict:
        if sentences is None:
            return {"score": 0, "each_score": [0]}
        """
        1. idf 找出每個段落 sentences 的 idf_words 的位置
        2. 找出每個段落 sentences 的態度詞位置
            1. 找到態度詞後，與所有 idf_words 位置相減取得距離
        """
        # 找出 IDF 關鍵字的所在地
        idf_in_sentences_location = self.find_idf_words_location(sentences, idf_words)
        # 將查詢句當中的醫療用詞剔除在正反向集合以外
        self.find_query_string_has_med_word(query_string=query_string)
        # 計算本文章的分數
        ret = self.judge_sentences(sentences, idf_dict, idf_in_sentences_location, idf_sum)
        self.except_med_words = set() # 回復原本
        return ret

    def find_idf_words_location(self, sentences: [str], idf_words: set):
        ret = []
        for sentence in sentences:
            idf_in_sentence = []
            for counter, char in enumerate(sentence):
                if char in idf_words:
                    idf_in_sentence.append(counter)
            ret.append(idf_in_sentence)
        return ret

    def find_query_string_has_med_word(self, query_string: str):
        counter = 0
        len_limit = len(query_string)
        prev_substring = ""
        substring = ""
        prev_res = set()
        while counter < len_limit:
            char = query_string[counter]
            substring += char
            res = set(filter(lambda x: substring in x, self.myDict.total_med_all_words))
            if res:
                prev_substring = substring
                prev_res = res.copy()

            else:
                if len(substring) > 1:
                    counter -= 1
                if prev_substring != "" and prev_substring in prev_res:
                    self.except_med_words.add(prev_substring)
                substring = ""
                prev_substring = ""
                prev_res = set()
            counter += 1
        return


    def judge_sentences(self, sentences: [str], idf_dict: dict, idf_in_sentences_location: [list], idf_sum: float):
        score = []
        total_score = 0.0
        for counter, sentence in enumerate(sentences):
            ret = self.judge_sentence(sentences[counter], idf_dict, idf_in_sentences_location[counter], idf_sum)
            total_score += ret
            score.append(ret)
        return {"score": total_score, "each_score": score}

    def judge_sentence(self, sentence: str, idf_dict: dict, idf_in_sentence_location: [int], idf_sum: float) -> float:
        if sentence is None or idf_in_sentence_location is None:
            return 0.0
        start_char_index = 0
        prev_substring = ""
        substring = ""
        prev_res = set()
        score = 0.0
        tmp_score = 0.0
        logging.info("Now Sentence is %s:", sentence)
        counter = 0
        len_limit = len(sentence)
        while counter < len_limit:
            char = sentence[counter]
            if char == '?' or char == '？':  # 標點符號判斷：問句
                tmp_score = 0.0
                substring = ""
                prev_substring = ""
                prev_res = set()
                counter += 1
            elif char == '。' or char == '，' or char == '！' or char == '!' or char == ',':  # 標點符號，代表一句話結束
                substring = ""
                if prev_substring != "" and prev_substring in prev_res:
                    delta = self.single_word_score(sentence, prev_substring, idf_dict, idf_sum, start_char_index,
                                                   counter, idf_in_sentence_location)  # 將剛剛結果的詞作分數計算
                    tmp_score += delta  # 分數加入
                prev_substring = ""
                prev_res = set()
                score += tmp_score  # 暫存分數加入句子分數
                tmp_score = 0.0  # 並且歸零
                counter += 1
                start_char_index = counter
            else:  # 如果不是碰到標點符號
                substring += char
                res = set(filter(lambda x: substring in x, self.myDict.total_all_words))
                logging.debug("Now Substring %s", substring)
                if res:
                    logging.debug("Result %s", res.__str__())
                    prev_substring = substring
                    prev_res = res.copy()
                    counter += 1
                else:
                    if prev_substring != "" and prev_substring in prev_res:
                        delta = self.single_word_score(sentence, prev_substring, idf_dict, idf_sum, start_char_index,
                                                       counter, idf_in_sentence_location)
                        tmp_score += delta
                        counter = start_char_index + len(prev_substring) - 1
                    elif len(substring) >= 1:
                        counter = start_char_index
                    substring = ""
                    prev_substring = ""
                    prev_res = set()
                    counter += 1
                    start_char_index = counter
        score += tmp_score
        return score

    def single_word_score(self, sentence, prev_substring, idf_dict, idf_sum, start_char_index, counter,
                          idf_in_sentence_location):
        delta = 0.0
        if prev_substring in self.except_med_words:
            return 0.0
        # print(start_char_index, counter, sentence[start_char_index:counter + 1], prev_substring)
        # assert(sentence[start_char_index:counter + 1] == prev_substring)
        distances = []
        for i in idf_in_sentence_location:
            this_word_score = idf_dict[sentence[i]] / idf_sum
            distances.append(word_distance(start_char_index, counter, i))
            this_word_score /= word_distance(start_char_index, counter, i)
            delta += this_word_score
        logging.debug("Distances: %s", distances.__str__())
        delta /= len(idf_in_sentence_location)
        delta *= self.myDict.dictionaryScore[prev_substring]
        logging.info("%s, %f", prev_substring, delta)
        return delta
