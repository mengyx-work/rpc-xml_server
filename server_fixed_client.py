from xmlrpclib import ServerProxy
from cmd import Cmd
from server import Node
import random, string, os, time, sys
from multiprocessing import Process
from util import GenPassword

SECRET_LENGTH = 10
HEAD_START = 1 # unit: second

class Client(Cmd):
    '''
    a text-based interface to the Node class, using cmd to
    create the Command line interface.
    '''
    prompt = 'Node > '

    def __init__(self, url, dirname, urlfile):
        
        Cmd.__init__(self)
        self.secret = GenPassword(SECRET_LENGTH)
        n = Node(url, dirname, self.secret)
        p = Process(target = n._start_server, name = 'rpc-xml_server')
        p.daemon = True
        p.start()
        time.sleep(HEAD_START)

        self.server = ServerProxy(url)

    def do_fetch(self, arg):
        print 'the fetch result: ', self.server.fetch(arg, self.secret)
        '''
        try:
            self.server.fetch(arg, self.secret)
        except:
            print 'failed to fetch ' + arg
        '''
    
    def do_exit(self, arg):
        sys.exit()

def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()

if __name__ =='__main__': main()
