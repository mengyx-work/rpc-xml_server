from xmlrpclib import ServerProxy
from cmd import Cmd
import random, string, os, time, sys
from multiprocessing import Process
import util

'''
a randomly generated password is shared among all server and clients 
each time of runing this package.
credential requirement:
1. each server requires credential for accessing certain
remote procedure calls such as fetch data and request URL
2. some API call may not need any credentials
3. each client has a credential for accessing all the servers


structure for this rpc-xml server and client
1. there are multiple independent servers using different credentials.
2. there are also multiple clients that are able to access each server
by the proper query credentials.
'''

class Client(Cmd):

    def __init__(self, dict_key, url=None):
        yml_data = util.GenYamlData(dict_key)
        self.secret = yml_data['server_password']
        self.url = url

    def do_connect_url(self, arg):
        # has to assume arg is a valid URL
        self.server = ServerProxy(arg)

    def do_fetch(self, arg):
        try:
            self.server.fetch(arg, self.secret)
        except:
            print 'failed to fetch ' + arg
    

def main():
    dict_key, url = sys.argv[1:]
    client = Client(dict_key, url)
    client.cmdloop()

if __name__ =='__main__': main()
