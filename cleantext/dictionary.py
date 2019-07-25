import nltk
import pickle
from collections import Counter
from helpfunctions import words
from proceedings import get_proceedings
import unicodedata

dictionary = Counter()
dictionary.update([i.rstrip()
                   for i in words(open('cleantext/etc/dict.txt').read())])
lemma = nltk.wordnet.WordNetLemmatizer()

freq = {}
freq2 = {}

try:
    # try loading a cached version first;
    # make it and store it, if it does not exist
    freq = pickle.load(open("pkls/freq.pkl"))
    freq2 = pickle.load(open("pkls/freq2.pkl"))
except Exception:
    for paper in get_proceedings():
        mywords = words(paper.text)
        for word in mywords:
            if word in freq2:
                freq2[word] += 1
            else:
                freq2[word] = 1

        words_unique = list(set(mywords))
        for word in words_unique:
            if word in freq:
                freq[word] += 1
            else:
                freq[word] = 1

    pickle.dump(freq, open("pkls/freq.pkl", 'w'))
    pickle.dump(freq2, open("pkls/freq2.pkl", 'w'))


def in_dictionary(word_orig):
    word = word_orig.lower()

    # number
    try:
        float(word)
        return True
    except BaseException:
        pass

    # reference
    if '[' in word and ']' in word:
        return True

    # fraction
    if '/' in word:
        try:
            num, den = word.split('/')
            float(num)
            float(den)
            return True
        except Exception:
            pass
        # either/or
        try:
            fst, snd = word.split('/')
            return in_dictionary(fst) and in_dictionary(snd)
        except Exception:
            pass

    if '-' in word:
        try:
            words = word.split('-')
            return all(in_dictionary(w) for w in words)
        except Exception:
            pass

    # stats
    if word_orig[0:2] == "F(":
        return True

    if word[-2:] == "'s" or word[-2:] == "s'":
        word = word[:-2]

    if word.isdigit() or word.isspace() or len(word) <= 1:
        return True

    word = str(word).translate(None, '!@#$(){}[],":')
    if (word in dictionary) or (lemma.lemmatize(word)
                                in dictionary) or (word.strip('.') in dictionary):
        return True

    # check for same mistake across several papers
    try:
        f1 = freq[word_orig]
        f2 = freq2[word_orig]
        return f1 >= 5 or f2 >= 15
    except Exception:
        return False
    return False
