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
class Client(object):

    OK = 0
    FAIL = 1

    def __init__(self, dict_key, url = None):
        yml_data = util.GetYamlData(dict_key)
        self.secret = yml_data['server_password']
        if url is not None:
            self.url = url
            self.server = ServerProxy(self.url)

    def getURL(self):
        if hasattr(self, 'url'):  return self.url
        return None

    def setURL(self, url):
        self.url = url
        self.server = ServerProxy(self.url)
        print 'current server URL is updated to %s' % self.url

    def fetch_from_server(self, query):
        if not hasattr(self, 'server'):
            print 'server is not connected yet. \n'
            return self.FAIL
        try:
            code, data = self.server.fetch(query, self.secret)
            if code == self.OK:
                return data
            else:
                sys.stderr.write('failed to use fetch %s \n' % query)
        except:
            print 'failed to call fetch! \n'

    def add_new_url(self, new_url):
        if not hasattr(self, 'server'):
            print 'server is not connected yet. \n'
            return self.FAIL
        try:
            code, data = self.server.add_known_url(new_url, self.secret)
            if code == self.OK:
                return data
            else:
                print 'failed to add URL %s' % new_url
        except:
            print 'failed to call add_known_url'
 
 

class Cmd_Client(Client, Cmd):

    prompt = 'rpc-xml_client > '

    def __init__(self, dict_key):
        Cmd.__init__(self)
        Client.__init__(self, dict_key)

    def do_show_url(self, arg):
        print 'the current URL: ', self.getURL()

    def do_set_url(self, url):
        # has to assume given url is a valid URL
        self.setURL(url)

    def do_fetch(self, arg):
        fetched_content = self.fetch_from_server(arg)
        if fetched_content is not None:
            print 'the content:\n  %s \n is fetched' % fetched_content

    def do_add_new_url(self, arg):
        self.add_new_url(arg)
   
    def do_exit(self, arg):
        sys.exit()


def main():
    #dict_key = sys.argv[1]
    dict_key = 'rpc-xml_server'
    print 'the dict_key: ', dict_key
    client = Cmd_Client(dict_key)
    client.cmdloop()

if __name__ =='__main__': main()
