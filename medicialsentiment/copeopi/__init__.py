import os
import sys
import csv
import json
import time
import uuid
import logging
import subprocess

from ckiptagger import data_utils, WS, POS, NER
from typing import List


class CopeOpi:
    def __init__(self, ws, pos, ner):
        self.data_path = os.path.dirname(os.path.abspath(__file__))
        self.ws = ws
        self.pos = pos
        self.ner = ner

    def dataFilePath(self, text: str):
        return os.path.join(self.data_path, text)

    def getOpinionScore(self, obj: dict):
        if obj["sentence"] is None:
            return {"score": 0, "eachScore": [0]}
        taskIDGroup: List[str] = list(str(uuid.uuid5(uuid.NAMESPACE_DNS, i)) for i in obj["sentence"])
        eachScore = []
        prev = os.getcwd() # java execute program, maybe can remove
        os.chdir(self.data_path) # java execute program, maybe can remove
        for i, element in enumerate(taskIDGroup):
            sentence_list = obj["sentence"][i]
            word_sentence_list = self.ws([sentence_list])
            pos_sentence_list = self.pos(word_sentence_list)

            def print_word_pos_sentence(word_sentence, pos_sentence, fileop):
                assert len(word_sentence) == len(pos_sentence)
                for word, pos in zip(word_sentence, pos_sentence):
                    print(f"{word}({pos})", end=" ", file=fileop)
                return

            with open(self.dataFilePath(taskIDGroup[i] + ".txt"), "w", encoding="utf-8") as op:
                print_word_pos_sentence(word_sentence_list[0], pos_sentence_list[0], op)
                print(file=op)
            subprocess.run(["java", "-cp", "./opinion/*.jar:.", "CopeOpi_trad", self.dataFilePath(taskIDGroup[i])])
            with open(self.dataFilePath(taskIDGroup[i] + ".csv")) as csvFile:
                rows = csv.reader(csvFile, delimiter=',')
                rows = list(rows)
                try:
                    eachScore.append(float(rows[0][1]))
                except IndexError:
                    print("WTF???")
            subprocess.run(["rm", self.dataFilePath(taskIDGroup[i] + ".csv"), self.dataFilePath(taskIDGroup[i] + ".txt")])
        os.chdir(prev) # java execute program, maybe can remove
        total = 0.0
        for i in eachScore:
            total += i
        total /= len(eachScore)
        return {"score": total, "eachScore": eachScore}
