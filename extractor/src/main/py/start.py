import optparse
from optparse import OptionGroup
from service import main
import cherrypy
import sys
import pickle
import os
from classifier import Classifier
from classifier import ClassifierException

if os.path.isdir("utils/"):
    sys.path.append("utils/")

optparser = optparse.OptionParser()

optHttpGroup = OptionGroup(optparser, "HTTP Server")

optHttpGroup.add_option("--listen-ip", action="store", dest="listen_ip", 
    help="IP Address to listen for connections, defaults to 0.0.0.0", 
    default="0.0.0.0"
)
optHttpGroup.add_option("--port", action="store", dest="http_port", 
    help="HTTP Port number, defaults to 21212", 
    default=21212, type="int"
)

optClassifierGroup = OptionGroup(optparser, "Classifier")

optClassifierGroup.add_option("--on-demand", action="store_true", dest="classifier_on_demand", 
    help="If enabled, the classifier will be loaded on demand, instead of in memory when the service is started."
)
optClassifierGroup.add_option("--pki-file", action="store", dest="pki_file", 
    help="Location of the classifier PKI file"
)

optparser.add_option_group(optHttpGroup)
optparser.add_option_group(optClassifierGroup)

def verify_required_opts(options):
    if options.pki_file == None:
        print "You must supply the location of the PKI file"
        sys.exit(1)

if __name__ == '__main__':
    
    (options, optargs) = optparser.parse_args()
    
    verify_required_opts(options)
    
    conf = {
        'global': {
            'server.socket_host': options.listen_ip,
            'server.socket_port': options.http_port
        },
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    
    kl = not options.classifier_on_demand
    
    print "Loading classifier (you should probably go get that cup of coffee now)..."
    
    classifier = Classifier()
    classifier.loadClassifier(options.pki_file)
        
    class Root():
        pass
    
    
    root = Root()
    root.extract = main.Extract(classifier)
    
    cherrypy.quickstart(root, '/', conf)
