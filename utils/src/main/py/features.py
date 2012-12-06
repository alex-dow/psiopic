import nltk
import random
import itertools

from nltk.tokenize.regexp import WordPunctTokenizer
from nltk.corpus.reader.util import read_blankline_block
import StringIO

def bigram_feats(words, listsize):
    """
    Gets a list of bigram features from a list of words
    """
    bigram_finder = nltk.collocations.BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(nltk.metrics.BigramAssocMeasures.chi_sq, listsize)
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])

def get_word_distribution(wordlist):
    """
    Organize list of words starting from most frequent, to least frequent.
    """
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

def document_as_words(document):
    """
    There is probably an NLTK function somewhere that does already, but I
    couldn't find it.
    
    So this just converts a single document into a list of words which you
    can then use with the rest of these functions, to get a feature list
    which you can then classify.
    """ 
    stringbuf = StringIO.StringIO(document)
    
    word_tokenizer = WordPunctTokenizer()
    para_tokenizer = read_blankline_block
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    
    words = []
    
    for para in para_tokenizer(stringbuf):
        for sent in sent_tokenizer.tokenize(para):
            for word in word_tokenizer.tokenize(sent):
                words.append(word)
                
    return words
    

def get_corpus_documents(corpus_root):
    """
    Get a list of documents from a corpus.
    
    Documents in this case, are being represented by a list of words
    contained in the document. No filtering is done on this list of words.
    
    The corpus root is expected to be a directory, containing subdirectories
    per category, and in each subdirectory, plaintext documents ending in
    *.txt
    
    All other functions in this module that require documents, execpts a list
    prepared by this function.
    """
    
    # TODO: Filename and category pattern should be function arguments
    corpus = nltk.corpus.CategorizedPlaintextCorpusReader(corpus_root,r'.*\.txt', cat_pattern=r'(\w+)/*')
    
    documents = []
    
    for category in corpus.categories():
        for fileid in corpus.fileids(category):
            documents.append((list(corpus.words(fileid)), category))
    random.shuffle(documents)
    return documents

def get_corpus_words(documents):
    """
    Puts together a list of all words in the entire corpus.
    """
    all_words = []
    
    for (words,cat) in documents:
        all_words.extend(words)
    
    return get_word_distribution(all_words)

def get_corpus_features(documents):
    """
    Will create a list of word features based on the corpus.
    
    The list of words will have the top 50 corpus words removed,
    the top 200 bigrams, top 2000, per corpus category
    """

    all_words = get_corpus_words(documents)[:50]
    filtered_words = []
    
    for k,t in documents:
        wordlist = []
        for word in k:
            if (word not in nltk.corpus.stopwords.words('english') and word not in all_words):
                wordlist.append(word)
        
        if len(wordlist) > 0:
            filtered_words.append((wordlist,t))
            
    bigrams = [(bigram_feats(words,200), category) for (words,category) in filtered_words]
    words   = [(word_feats(words, 2000), category) for (words,category) in filtered_words]
    return bigrams + words

def word_feats(words, listsize=2000):
    """
    Fetches the top [listsize] amount of words, ordered
    by distribution frequency.
    """
    retval = []

    for word in get_word_distribution(words)[:listsize]:
        w = word.lower()
        retval.append((w, True))

    return dict(retval)

def get_training_set(features, testsize = 0):
    """
    Prepares a training set for a classifier. Returns a tuple where
    first key is the training set, second key is the testing set.
    
    If the test size is 0, then the feature list will just be returned.
    
    If the test size is a float between 0 and 1, it will be treated as a
    percentange.
    """
    if testsize == 0:
        return (features, [])
    
    if testsize > 1:
        cutoff = int(testsize)
    else:
        cutoff = int(len(features) * testsize)
    test_set, train_set = features[:cutoff], features[cutoff:]
    return (train_set, test_set)