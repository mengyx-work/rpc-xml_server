from SimpleXMLRPCServer import SimpleXMLRPCServer

s = SimpleXMLRPCServer(("", 4242))
def double(x):
    return x * 2
s.register_function(double)
s.serve_forever()
