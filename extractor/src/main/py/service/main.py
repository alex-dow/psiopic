import os
import cherrypy
import simplejson as json

class Extract():
    
    exposed = True
    
    def __init__(self, classifier):
        self._classifier = classifier
        
    def getRequestContent(self):
        request = cherrypy.request
        
        if request.headers['content-type'] == 'application/x-www-form-urlencoded':
            return request.params['content']
        else:
            return request.body.read()
            
    def POST(self):
        
        reqcontent = self.getRequestContent()
        
        cats = self._classifier.getCategoryProbabilityFromDocument(reqcontent)
                    
        results = sorted(cats, reverse=True)
        
        return json.dumps(results)

        
