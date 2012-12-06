                                    __                          
                                __ /\ \                         
                _____     ____ /\_\\ \ \/'\      ___     ___    
               /\ '__`\  /',__\\/\ \\ \ , <     / __`\ /' _ `\  
               \ \ \L\ \/\__, `\\ \ \\ \ \\`\  /\ \L\ \/\ \/\ \ 
                \ \ ,__/\/\____/ \ \_\\ \_\ \_\\ \____/\ \_\ \_\
                 \ \ \/  \/___/   \/_/ \/_/\/_/ \/___/  \/_/\/_/
                  \ \_\                                         
                   \/_/                                         
                   
                    PRESENTS:
                    
                    Psiopic v0.1 Development
                    

Psiopic
=======

Intro
-----
This is not a packaged version of Psiopic, it is a development version. If you
do not want to fuss with running a maven install, then visit
http://github.com/v0idnull/psiopic and download a pre-built package of Psiopic.

Installation
------------
Psikon's maven repositories are not working yet. So, you'll have to install the
parent POM before installing the whole shebang:

    $ cd parent
    $ mvn install
    ...
    $ cd ..
    $ mvn install

Doing this, you'll have a built package in:
~/.m2/repository/com/psikon/psiopic/package/0.1-SNAPSHOT/package-0.1-SNAPSHOT.zip

You will also have to install the necessary python dependencies:

* numpy
* cherrypy
* nltk
* simplejson

    $ easy_install pip
    $ pip install numpy cherrypy nltk simplejson
    
Usage
-----
Refer to the README in package/src/main/resources
    
Resources
---------
NLTK: http://nltk.org/
CherryPy: http://www.cherrypy.org/




