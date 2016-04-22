from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import ServerProxy
from os.path import isfile, join
from os import listdir
import sys

from urlparse import urlparse
'''
 to start the client by:
 python client.py urls.txt directory http://servername.com:4242

urls.txt, a text file to gives a list of known URLs for the client server/node to 
establish the connection

directoy, a path where the available resource is stored

http://servername.com:4242: the port is 4242
'''

## top-level function is similar to a class static method
def getPort(url):
    # reference https://docs.python.org/2/library/urlparse.html
    parsed_url = urlparse(url)
    if parsed_url.port != None:
        return parsed_url.port
    raise ValueError('failed to find port in URL' + str(url))


class Node(object):
    OK = 0
    FAIL = 1
    MAX_HISTORY_LENGTH = 6
    EMPTY = ''

    SimpleXMLRPCServer.allow_reuse_address = 1
    
    def __init__(self, URL = None, dirname = './', secret = None):
        self.secret = secret
        self.URL = URL
        self.dirname = dirname
        # set for known URLs (neighbors)
        self.known = set()

    # function to start the server side for node
    def _start_server(self):

        # fake the server to be local
        #server = SimpleXMLRPCServer((self.URL, getPort(self.URL)))
        server = SimpleXMLRPCServer(("", getPort(self.URL)))

        # server.register_function(self.fetch)
        server.register_instance(self) # register an object instread of function
        server.serve_forever()


    def _handle(self, query):
        filename = join(self.dirname, query)
        ## list all the files
        #all_files = [f for f in listdir(self.dirname) if isfile(join(self.dirname, f))]
        if isfile(filename): return self.OK, open(filename).read()
        return self.FAIL, self.EMPTY

    def _broadcast(self, query, history):
        for URL in self.known.copy(): ## to delete URL without any response, so a copy is needed
            if URL in history: continue
            try:
                s = ServerProxy(URL)
                ## security issue with register_instance, all the method exposed to the RPC calls
                code, data = s.query(query, history)
                if code == self.OK: return code, data
            except:
                self.known.remove(URL)

        return self.FAIL, self.EMPTY

    def query(self, query, history = []):
        '''
        look for the requested file in local directory.
        1. use _handle to process query locally
        2. use _broadcast to pass query to neighbors in self.knowns
        '''
        code, data = self._handle(query)
        print 'code from _handle', code
        if code == self.OK: return code, data
        history = history + [self.URL]
        # constrain on the history length
        if len(history) > MAX_HISTORY_LENGTH:
            return self.FAIL, self.EMPTY
        return self._broadcast(query, history)


    def fetch(self, query, secret):
        '''
        function to fetch query file either locally or the known URLs.
        the secret is required
        '''
        if secret != self.secret: return 1
        code, data = self.query(query)
        print 'the code and data: ', code, data
        if code == self.OK:
            #f = open(join(self.dirname, query), 'w')
            f = open('./tmp.txt', 'w')
            f.write(data)
            f.close()
            return data
        else:
            return self.FAIL

    def hello(self, other_URL):
        '''
        function to build connection from other URL
        '''
        self.known.add(other_URL)
        return self.OK

def main():
    url, dirname, secret = sys.argv[1:]
    node = Node(url, dirname, secret)
    node._start_server()

if __name__ == '__main__': main()
