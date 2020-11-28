import logging


class WordScore(object):
    def __init__(self, start_index, end_index, word, score, has_change=False):
        self.__start_index = start_index
        self.__end_index = end_index
        self.__word = word
        self.__score = score
        self.__change = has_change

    def change_score(self) -> bool:
        if not self.__change:
            self.__change = True
            self.__score = -self.__score
            return True
        else:
            logging.warning("%s doesn't change score, beacuse it has been change", self.__word)
            return False

    def has_change(self):
        return self.__change

    def get_score(self):
        return self.__score

    def get_start_index(self):
        return self.__start_index

    def get_end_index(self):
        return self.__end_index
