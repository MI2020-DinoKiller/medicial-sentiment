class FindWord(object):
    def __init__(self):
        self.list_sets: [set] = []
        self.list_words: [str] = []
        self.last_has_words_index = -1

    def append(self, word, sets):
        self.list_words.append(word)
        self.list_sets.append(sets)
        if word in sets:
            self.last_has_words_index = len(self.list_sets) - 1
        return

    def recall(self):
        if self.last_has_words_index != -1:
            return self.list_words[self.last_has_words_index]
        return None

    def is_empty(self):
        return self.last_has_words_index == -1

    def clear_all(self):
        self.list_sets.clear()
        self.list_words.clear()
        self.last_has_words_index = -1
