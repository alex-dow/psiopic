import nltk
import pickle

from features import document_as_words
from features import bigram_feats, word_feats

class Classifier(object):
    
    _nltkClassifier = None
    _pki_file = None
    
    keep_loaded = True
    
    def __init__(self, keep_loaded=True):
        self.keep_loaded = keep_loaded
            
    def loadClassifier(self, pki_file):
        try:
            if self.keep_loaded and self._nltkClassifier != None:
                return self._nltkClassifier
            
            fModel = open(pki_file,'rb')
            self._nltkClassifier = pickle.load(fModel)
            fModel.close()
        except IOError as e:
            if e.errno == 2:
                raise ClassifierException('The classifier file could not be found')
            else:
                raise ClassifierException('There was a problem trying to load the classifier: ' + e.strerror)
        
    def saveClassifier(self, pki_file, classifier):
        try:
            fModel = open(pki_file,'wb')
            pickle.dump(classifier,fModel,1)
            fModel.close()
        except Exception as e:
            raise ClassifierException("There was a problem trying to save the classifier: " + str(e))
        
    def getCategoryFromDocument(self, document):
        
        if self._nltkClassifier == None:
            raise ClassifierException("The classifier must first be loaded by the loadClassifier() method")
        
        docwords = document_as_words(document)
        topic = self._nltkClassifier.classify(docwords)
        return topic
    
    def getCategoryProbabilityFromDocument(self, document):
        
        if self._nltkClassifier == None:
            raise ClassifierException("The classifier must first be loaded by the loadClassifier() method")
        
        docwords = [word for word in document_as_words(document) if word not in nltk.corpus.stopwords.words('english')]
        
        bigrams = bigram_feats(docwords,200)
        words = word_feats(docwords,2000)
        
        
        
        featureset = dict(bigrams.items() + words.items())
        
        probdist = self._nltkClassifier.prob_classify(featureset)
        
        results = []
        samples = probdist.samples()
        for i in samples:
            prob = probdist.prob(i)
            if (prob >= 0.001):
                results.append((probdist.prob(i),i))
                    
        results = sorted(results, reverse=True)
        return results        
            
class ClassifierException(BaseException):
    pass
