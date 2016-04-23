from SimpleXMLRPCServer import SimpleXMLRPCServer
from multiprocessing import Process
from xmlrpclib import ServerProxy
from os.path import isfile, join
from os import listdir
import sys, yaml, util
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

        server.register_function(self.fetch)
        server.register_function(self.add_known_url)
        '''
        register an instance intead of specific function, 
        will expose all the functions to the remote RPC calls
        '''
        # server.register_instance(self) 
        server.serve_forever()


    def _handle(self, query):
        '''
        handle the local query search
        '''
        filename = join(self.dirname, query)
        ## list all the files
        #all_files = [f for f in listdir(self.dirname) if isfile(join(self.dirname, f))]
        if isfile(filename): return self.OK, open(filename).read()
        return self.FAIL, self.EMPTY

    def _broadcast(self, query, history):
        '''
        handle the query search fro other known URLs
        '''
        for URL in self.known.copy(): ## to delete URL without any response, so a copy is needed
            if URL in history: continue
            try:
                s = ServerProxy(URL)
                ## fetch is the only registered function
                code, data = s.fetch(query, self.secret, history)
                if code == self.OK: return code, data
            except:
                self.known.remove(URL)

        return self.FAIL, self.EMPTY

    def _query(self, query, history = []):
        '''
        look for the requested file in local directory.
        1. use _handle to process query locally
        2. use _broadcast to pass query to neighbors in self.knowns
        '''
        code, data = self._handle(query)
        # print 'code from _handle', code
        if code == self.OK: return code, data
        history = history + [self.URL]
        # constrain on the history length
        if len(history) > self.MAX_HISTORY_LENGTH:
            return self.FAIL, self.EMPTY
        return self._broadcast(query, history)

    def add_known_url(self, url, secret):
        if secret != self.secret: return self.FAIL, 'passowrd is incorrect!'
        if url in self.known:
            return self.FAIL, 'already in the known URLs.'
        else:
            self.known.update(url)
            return self.OK, self.URL

    def fetch(self, query, secret, history = None):
        '''
        function to fetch query file either locally or the known URLs.
        the secret is required
        '''
        if secret != self.secret: return self.FAIL, 'password is incorrect!' 
        if history is not None:
            code, data = self._query(query, history)
        else:
            code, data = self._query(query)
        ## print 'the code and data: ', code, data
        if code == self.OK:
            #f = open(join(self.dirname, query), 'w')
            f = open('./query_result.txt', 'w')
            f.write(data)
            f.close()
            return self.OK, data
        else:
            #return self.FAIL
            return self.FAIL, 'failed to fetch %s' % query

    def exchange_url(self, other_UR):
        '''
        function to build connection from other URL
        '''
        s = ServerProxy(other_UR)
        code, data = s.add_known_url(self.URL, secret)
        if code == self.FAIL:
            return code, data
        else:
            self.known.append(data)
            return self.OK, 'successfully added URL %s' % data


def main():
    '''
    use multiprocessing to create a separate process
    for this server daemon
    '''
    server_data = util.GetYamlData('rpc-xml_server')
    url, dirname  = sys.argv[1:]
    n = Node(url, dirname, server_data['server_password'])
    p = Process(target = n._start_server, name = 'rpc-xml_server_%s' % server_data['server_name'])
    p.daemon = True
    p.start()
    p.join() ## make the main as daemon 

if __name__ == '__main__': main()
