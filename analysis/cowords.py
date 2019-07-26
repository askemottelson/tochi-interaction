from proceedings import get_proceedings
from nltk.tokenize import sent_tokenize
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
wordnet_lemmatizer = WordNetLemmatizer()


stopwords = set(
    stopwords.words('english') +
    ["eg","the","of","to","and","a","in","for","that","is","we","with","as","on","this","be","are","by","was","or","an","were","it","from","their","not","they","our","can","more","have","at","which","these","one","also","when","each","how","used","use","other","such","but","between","all","using","two","than","about","would","has","different","work","i","could","may","had","while","if","there","some","only","into","both","what","new","been","most","however","will","who","where","them","its","first","because","many","three","then","no","so","figure","paper","within","like","well","way","might","literature","see","open","even","approach","1","2","3","particular","ways","rather","make","often","found", "without", "provide", "thus", "significant", "ie", "u", "mean", "term", "difference", "whole", "another", "second", "first", "third", "others", "previous", "much", "specific", "across", "important", "take", "=", "4", "although", "several", "current", "better", "one", "range", "main", "page", "whether", "le", "able", "due", "include", "existing", "allow", "line", "rate", "allows", "given", "single", "addition", "benefit", "four", "instance", "5", "provides", "us", "developed", "6", "b", "providing", "&", "discussion", "therefore", "describe", "v", "/", "c", "al", "finally", "yet"]
)

def e(i):
    return str(i).encode('ascii', 'ignore').lower().replace(",","").replace(".", "").replace(";","").replace(":","").replace("(","").replace(")","").replace("'s","")

all_nouns = set([x.name().split('.', 1)[0] for x in wn.all_synsets('n')])

if __name__ == "__main__":
    proceedings = get_proceedings(min_year=1980, max_year=2019)

    keywords = set(["embodied", "embody", "body", "bodies"])
    cnt = Counter()
    nouns = Counter()

    for paper in proceedings:

        sentences = sent_tokenize(paper.clean_text)

        for sentence in sentences:
            words = e(sentence).split()

            for word in words:
                if word in keywords:
                    r = [wordnet_lemmatizer.lemmatize(w) for w in words if w not in stopwords.union(keywords)]
                    cnt.update(r)
                    nouns.update([x for x in r if x in all_nouns])
                    break

    for w,c in cnt.most_common(500):
        print w,c
    print 70 * "*"
    for w,c in nouns.most_common(500):
        print w,c

    # Generate a word cloud image
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    # lower max_font_size
    wordcloud = WordCloud(background_color="white", width=800, height=400).generate_from_frequencies(cnt)
    
    plt.figure(figsize=(20,10), facecolor='k')
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("wc.png", bbox_inches='tight')
