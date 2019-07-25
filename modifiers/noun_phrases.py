import nltk
from proceedings import get_proceedings

#Noun phrase patterns
jk_patterns = """
    CONJ: {<TO|CC>*}
    PRE: {<CONJ>?<JJ.*>+}
        {<CONJ>?<NN.*>+}
    NP: {<PRE>*<ZZ>+<VB.*>*<PRE>*}
    """

#List of keywords of interest
interactions = ["interaction", "interactions", "interactional"]
words_interested = ["meaning", "meaningful"]

#Noun Phrase Chunker
NPChunker = nltk.RegexpParser(jk_patterns)


def assign_NP_sentence(tagged_sentence):
    nps = []
    tree = NPChunker.parse(tagged_sentence)

    for subtree in tree.subtrees():

        #If the subtree is our desired noun phrase
        if subtree.label() == 'NP':
            #Grab noun phrase from leaves, keeping correct instance of 'interaction' highlighted

            nps.append(" ".join([word for word, tag in subtree.leaves()]))
            
    return nps


def parse_sentence(sentence):
    #Tag each word with grammar label
    sentence_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
    words = [w[0] for w in sentence_tagged]

    # only "interaction" sentences
    #if any(w in interactions for w in words):
    res = []
            
    #Loop through the labelled words
    for idx, sent in enumerate(sentence_tagged):

        if sent[0] in interactions:

            #Replace interaction word with *interaction* and update grammar tag to ZZ
            temp = list(sentence_tagged[idx])
            temp[1] = 'ZZ'
            temp[0] = "*interaction*"
            sentence_tagged[idx] = tuple(temp)

    #Check sentence grammar against noun phrase pattern
    return assign_NP_sentence(sentence_tagged)


def go_easy():
    papers = get_proceedings(min_year=2016, max_year=2017)
    res = {}
    for paper in papers:
        sentences = nltk.sent_tokenize(paper.clean_text)
        for sentence in sentences:
            if ("meaningful" in sentence or "meaning" in sentence) and "interaction" in sentence:

                if not paper in res:
                    res[paper] = []
                res[paper].append(sentence)

    for paper in res.keys():
        print 2 * "\n"
        print 70 * "*"
        print paper.title, paper.year, paper.DOI
        print 70 * "*"
        for sent in res[paper]:
            print "+++ " + " ".join(sent.split())

def go_hard():
    papers = get_proceedings(min_year=2016, max_year=2017)
    res = {}
    for paper in papers:
        sentences = nltk.sent_tokenize(paper.clean_text)
        for sentence in sentences:
            grammar_sentences = parse_sentence(sentence)

            # meaning, meaningful
            meaning = False
            for g in grammar_sentences:
                if any(w in g for w in words_interested):
                    meaning = True

            if meaning:
                if paper not in res:
                    res[paper] = []
                res[paper].extend(grammar_sentences)

    for paper in res.keys():
        print 70 * "*"
        print paper.title, paper.year, paper.DOI
        grammar = res[paper]
        for grammar_sentences in grammar:
            print grammar




if __name__ == "__main__":
    go_easy()
    #go_hard()
