import sys
from datetime import datetime
import xml.sax
from subprocess import Popen
from subprocess import PIPE
import re
import os
import md5
from multiprocessing import Pool
import urllib2
import bz2
import optparse
from optparse import OptionGroup
from urlparse import urlparse
import shutil

def is_win():
    if os.name == "nt":
        return True
    return False 

if not is_win():
    import blessings

optparser = optparse.OptionParser(version="Psiopic 1.0")

optparser.add_option('--xml-url', action='store', dest="wikinews_url", 
    help="URL of the Wikinews XML dump. Defaults to the latest dump available", 
    default="http://dumps.wikimedia.org/enwikinews/latest/enwikinews-latest-pages-meta-current.xml.bz2"
)
optparser.add_option('--boilerclog', action="store", dest="boilerclog", 
    default="lib/boilerclog-1.0-SNAPSHOT.jar", 
    help="Location of the Boilerclog jar. Defaults to lib/boilerclog-1.0-snapshot.jar"
)
optparser.add_option('--corpus-dir', action="store", dest="corpus_dirname", 
    default="./corpus", 
    help="Path to store the final corpus. Defaults to a foler named corpus, one folder below the location of build_corpus.py"
)
optparser.add_option('--force', action="store_true", dest="force_dl", 
    help="Forces a download of the XML dump"
)
optparser.add_option('--max-children', action="store", dest="max_children", type="int", 
    default=5, 
    help="Maximum child processes to spawn"
)

optTweakGroup = OptionGroup(optparser, "Topics",
    "There is a default set of 7 news relates topics, however you can use the following to change which topics are extracted"
)

optTweakGroup.add_option("--topics", action="store", dest="tmp_topics", 
    help="List of wikinews categories, separated by a comma"
)

optparser.add_option_group(optTweakGroup)
(optoptions, optargs) = optparser.parse_args()

root_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
os.chdir(root_dir)
os.environ['PYTHONIOENCODING'] = 'utf-8'

# FIXME hard coded topics!
topics = ['Politics and conflicts','Crime and law','Economy and business','Science and technology','Culture and entertainment','Disasters and accidents','Sports']
topic_process = {}

spinner_icons = ['-','\\','|','/']
spinner_pos = 0

corpus_dirname = optoptions.corpus_dirname
max_children = optoptions.max_children
boilerclog   = optoptions.boilerclog
force_dl     = optoptions.force_dl

wikinews_url = optoptions.wikinews_url
wikinews_zip = os.path.basename(urlparse(wikinews_url).path)
wikinews_xml = wikinews_zip[:-4]



for t in topics:
    topic_process[t.replace(" ", "_")] = 0

if not is_win():
    term = blessings.Terminal()

class XmlPageHandler(xml.sax.ContentHandler):

    processing_ns = False
    processing_text = False
    
    pages = [""]
    current_page = 0
    
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.processing_ns = False
        self.processing_text = False
        self.processing_article = False
        
    def startElement(self, name, attrs):
        if name == "ns":
            # Inform characters() that we are getting characters from a ns tag
            self.processing_ns = True
            
        if name == "text" and self.processing_article == True:
            # Inform characters() that we are getting characters from a text tag
            # only do this, if we know we want to. We know we want to when
            # self.processing_article is True.
            self.processing_text = True
            self.processing_article = False
    
    def endElement(self, name):
        if name == "text":
            categories = get_categories(self.pages[self.current_page])
            
            if filter_categories(categories) == True:
                self.pages[self.current_page] = ""
            else:
                if not is_win():
                    spinner(len(self.pages))
                
                self.processing_text = False
                self.current_page += 1
                self.pages.append("")
    
        if name == "ns":
            self.processing_ns = False
        if name == "revision":
            self.processing_article = False
    
    def characters(self, content):
        
        if self.processing_ns == True and content == "0":
            # If the ns tag contains 0, then we know this is an article
            # we want to keep. We turn on processing_article so that when
            # we encounter a text tag, we'll know that this contains the article
            # we want.
            self.processing_article = True
            self.processing_ns = False
        
        if self.processing_text == True:
            # we get the article in chunks, so we'll 
            
            self.pages[self.current_page] += content


def get_spinner_icon():
    global spinner_icons
    global spinner_pos
    
    spin = spinner_icons[spinner_pos]
    
    spinner_pos += 1
    if spinner_pos >= len(spinner_icons):
        spinner_pos = 0
    
    return spin

def spinner(append = ""):
    # Create a space then the spinner, then move the cursor back to the space
    # Keeps the cursor from being over the spinner
    append = str(append)
    
    if not is_win():
        moveleft = ""
        if append != "":
            for x in range(0,len(append)):
                moveleft += str(term.move_left)
        
        moveleft += str(term.move_left) + str(term.move_left) + str(term.move_left)
        
        sys.stdout.write(" " + get_spinner_icon() + " " + append + moveleft)
        sys.stdout.flush()


def do_download(url, zipfile, xmlfile):
    sys.stdout.flush()
    global force_dl
    global wikinews_zip
    global wikinews_xml

    if force_dl:
        print "Forcing a download"
        download_file(url)
        decompress_file(wikinews_zip, wikinews_xml)
        return

    if os.path.isfile(xmlfile):
        answer = raw_input("Expected xml file found, do you want to download it again (y/N): ")
        if (answer.lower() == "n" or answer == ""):
            print "Skipping download"
        else:
            download_file(url)
            decompress_file(wikinews_zip, wikinews_xml)
    elif os.path.isfile(zipfile):
        answer = raw_input("Expected zip file found, do you want to download it again (y/N): ")
        if (answer.lower() == "n" or answer == ""):
            print "Skipping download"
            decompress_file(wikinews_zip, wikinews_xml)
        else:
            download_file(url)
            decompress_file(wikinews_zip, wikinews_xml)            
            
    else:
        download_file(url)
        decompress_file(wikinews_zip, wikinews_xml)
        
    

def decompress_file(src_file, target_file):
    
    sys.stdout.write("Decompressing: %s " % src_file)
    sys.stdout.flush()
    
    bz2file = bz2.BZ2File(src_file)
    
    f = open(target_file, "w")
    
    buffer_size = 4096
    
    interval = 1000
    cur_interval = 0
    
    while True:
        
        if (cur_interval == interval):
            spinner()
            cur_interval = 0
            
        cur_interval += 1
        
        bufferout = bz2file.read(buffer_size)
        if not bufferout:
            break
        
        f.write(bufferout)
        
        
        
    print ""
    f.close()
    
    
def download_file(url):
    
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name,'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-length")[0])
    
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    print ""
    sys.stdout.flush()
    
    buffer_size = 0
    prev_buffer_size = 0
    block_sz = 8192
    prev_interval = 0
    while True:
        cur_interval = datetime.now().second
        
        bufferout = u.read(block_sz)
        if not bufferout:
            break;
        buffer_size += len(bufferout)
        f.write(bufferout)
        
        if cur_interval - prev_interval >= 1:
            
            buffer_diff = buffer_size - prev_buffer_size
            prev_buffer_size = buffer_size
            
            buffer_speed = buffer_diff / 1024
            
            status = r"%10d  [%3.2f%%] %10d/kbps" % (buffer_size, buffer_size * 100. / file_size, buffer_speed)
            
            if not is_win():
                print term.move_up + status
            else:
                print status
                sys.stdout.flush()

        prev_interval = cur_interval
        
    f.close()
    
def filter_categories(categories):
    return True if len([cat for cat in categories if cat in topics]) != 1 else False
    
def get_categories(page):
    return re.findall("\[\[Category\:([a-zA-Z0-9_\s\-]+)\]\]", page)
    
def page_processor(page):
    """
    First get the categories from the page
  
    They are listed on the bottom of the text in this format:
    [[Category:Politics and conflicts]]
    """
    categories = get_categories(page)

    for m in categories:
        if m in topics:
            try:
                os.makedirs(corpus_dirname + "/" + m.replace(" ", "_"))
            except OSError as e:
                if e.errno != 17:
                    print e.strerror
                    return []
                    
    

    # TODO: It's not clear whether the replace here is necessary anymore
    wikicmd = Popen(["java","-jar",boilerclog], stdout=PIPE, stdin=PIPE)
    boilerout, wikicmd_stderr = wikicmd.communicate(input=page.replace("{{w|","{{w:").encode('utf-8'))
    
    """
    Here we want to strip out any remaining {{ }} stuff
    """
    cleanedContent = re.sub("(\{\{.*\}\})","",boilerout)
    
    if len(cleanedContent) < 250:
        return []

    filename = md5.new(m).hexdigest()

    for cat in categories:
        if cat in topics:
            f = open(corpus_dirname + "/" + cat.replace(" ","_") + "/" + filename + ".txt", "w")
            f.write(cleanedContent)
    sys.stdout.flush()
    return categories

def page_process_screen(categories):
    
    global topic_process
    global topics
    global term
    
    for cat in categories:
        if cat in topics:
            topic_process[cat.replace(" ", "_")] += 1
        
    if not is_win():
        for k, v in topic_process.iteritems():
            print "%30s: %5d" % (k.replace("_", " "), v)
        for i in range(0,len(topics)):
            sys.stdout.write(term.move_up)
        sys.stdout.flush()
        
    

if __name__ == "__main__":

    total_time_start = datetime.now()
    
    do_download(wikinews_url, wikinews_zip, wikinews_xml)
    
    
    print "Cleaning up previous job"
    
    try:
        shutil.rmtree(corpus_dirname)
    except OSError as e:
        if e.errno != 2:
            print e.strerror
            sys.exit(1)
    
    os.makedirs(corpus_dirname)
    
    sys.stdout.write("Fetching all relevant pages from xml database: ")
    sys.stdout.flush()
    
    f = open(wikinews_xml)
    xph = XmlPageHandler()
    try:
        xml.sax.parse(f, xph)
    except:
        pass
    
    pages = xph.pages
    f.close()
    
    print ""
    print "Total pages: %d" % len(pages)
    sys.stdout.flush()
    counter = 1
    total = len(pages)
    
    page_process_screen([])


    p = Pool(max_children)
    if not is_win():
        """
        We sacrifice a bit of performance to have a better UI
        In the future, we'll offer something to disable it
        """
        im = p.imap(page_processor, pages, 20)
        for what in im:
            page_process_screen(what)
        
        # page_process_screen will put the curser in a weird spot
        for i in range(0,len(topics)):
            sys.stdout.write(term.move_down)
        print " "
    else:
        p.map(page_processor, pages)

    total_time_delta = datetime.now() - total_time_start
    
    print ""
    print "Total time: %s" % total_time_delta


