import nltk
import sys
import collections
from datetime import datetime
import optparse
import os

from classifier import Classifier
from features import get_corpus_documents
from features import get_corpus_features
from features import get_training_set

def save_classifier(classifier, name, root_dir="./"):
    filename = root_dir + name + '.pki'
    cmodel = Classifier()
    cmodel.saveClassifier(filename, classifier)

start_time = datetime.now()

optparser = optparse.OptionParser()
optparser.add_option('--classifier-name', action="store", dest="classifier_name", 
    help="Name of classifier, used for filenames"
)
optparser.add_option('--classifier-dir', action="store", dest="classifier_dir",
    help="Path where to put the saved classifier", default="./"
)
optparser.add_option('--corpus-dir', action="store", dest="corpus_dir", default="./corpus",
    help="Location of the corpus directory"
)
optparser.add_option('--limit',action="store",dest="corpus_limit", type="int",
    help="Maximum number of documents per topic. Should be equal to the smallest topic you have."
)
optparser.add_option('--test-size',action="store",dest="test_size", type="float", 
    help="Number of documents to use for testing, set to 0 for none. If number is less than 1, then it will be treated as a percentage. Example: 0.25 would result in 25% of the corpus documents being used for testing instead of classifying."
)
optparser.add_option('--test-only',action="store_true",dest="test_only",
    help="If enabled, then the classifier will not be saved, just tested."
)
optparser.add_option('--show-expected-classification',action="store_true", dest="show_expected",
    help="If enabled, will show the list of expected classifications, and the list of classifications that was found, per test document"
)

(optoptions, optargs) = optparser.parse_args()

corpus_dir      = optoptions.corpus_dir
corpus_limit    = optoptions.corpus_limit
test_size       = optoptions.test_size
show_expected   = optoptions.show_expected
classifier_name = optoptions.classifier_name
classifier_dir  = optoptions.classifier_dir
test_only       = optoptions.test_only

print "Getting documents from corpus"
sys.stdout.flush()
docs = get_corpus_documents(corpus_dir)[:corpus_limit]

print "Getting corpus features"
sys.stdout.flush()
corpus_feats = get_corpus_features(docs)

print "Getting training set"
sys.stdout.flush()
training_set, test_set = get_training_set(corpus_feats, test_size)

print "Training set size: %d - Test set size: %d" % (len(training_set), len(test_set))
sys.stdout.flush()

print "Training classifier"
sys.stdout.flush()
classifier = nltk.NaiveBayesClassifier.train(training_set)

if test_size > 0:

    print "Testing classifier"
    sys.stdout.flush()
    probdistlist = []

    for testdoc in test_set:
        probdist = classifier.prob_classify(testdoc[0])
        results = []
        samples = probdist.samples()
        for i in samples:
            prob = probdist.prob(i)
            if (prob >= 0.001):
                results.append((probdist.prob(i),i))
                
        results = sorted(results, reverse=True)
        probdistlist.append((testdoc[1], results))

    print "Calculating metrics"
    sys.stdout.flush()
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)

    for i, (feats, label) in enumerate(test_set):
        refsets[label].add(i)
        observered = classifier.classify(feats)
        testsets[observered].add(i)

    accuracy = nltk.classify.util.accuracy(classifier, test_set)
    precision = {}
    recall = {}

    topics = refsets.keys()
    for cat in topics:
        precision[cat] = nltk.metrics.precision(refsets[cat], testsets[cat])
        recall[cat] = nltk.metrics.recall(refsets[cat], testsets[cat])

        if show_expected == True:
            print "--"
            for expected, results in probdistlist:
                print "Expected: " + expected + " -- Received: " + str(results)
    
            print "--"


    print " "
    print " "
    print " ---------------------------------------------------------------"
    print " -                          RESULTS                            -"
    print " ---------------------------------------------------------------"
    print " "
    print "    %-26s %-9s   %-9s" % ("Category","Precision","Recall")

    for cat in topics:
        print "    %-26s %-9.5f   %-9.5f" % (cat, precision[cat], recall[cat])

    print " "
    print "    %-26s %-9.5f" % ("Overall accuracy:", accuracy)
    sys.stdout.flush()


print " "
if test_only != True:
    print "Saving classifier"
    sys.stdout.flush()
    save_classifier(classifier, classifier_name, classifier_dir)

print "Dissolving my reality"
sys.stdout.flush()
classifier = None
training_set = None
test_set = None
docs = None
corpus_feats = None

end_time = datetime.now()
total_time = end_time - start_time

print "--"
print "%s %s" % ("Total time:", str(total_time))
print " "
sys.stdout.flush()
sys.exit(0)