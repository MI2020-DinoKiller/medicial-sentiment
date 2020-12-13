def content_cut_from_sentence(content: str, sentences: [str], scores: [float]):
    ret_sentences = []
    ret_scores = []
    st = 0
    for index, sentence in enumerate(sentences):
        get_index = content.find(sentence, st)
        if st != get_index:
            ret_sentences.append(content[st:get_index])
            ret_scores.append(0.0)
        ed = get_index + len(sentence)
        ret_sentences.append(content[get_index:ed])
        ret_scores.append(scores[index])
        st = ed
    if len(content) != st:
        ret_sentences.append(content[st:])
        ret_scores.append(0.0)
    return ret_sentences, ret_scores
