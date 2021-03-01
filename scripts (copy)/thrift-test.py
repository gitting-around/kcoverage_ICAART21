#!/usr/bin/env python
 
import sys
sys.path.append('..')
 
from SharedDefinitions9 import MmtService
from SharedDefinitions9 import PlannerService
from SharedDefinitions9.ttypes import *
from SharedDefinitions9.constants import *
 
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
 
import socket
 
class HelloWorldHandler(MmtService.Iface):
  def __init__(self):
    self.log = {}
 
  def ping(self):
    print "ping() or whatever"
 
  def sayHello(self):
    print "sayHello()"
    return "say hello from " + socket.gethostbyname(socket.gethostname())
 
  def sayMsg(self, msg):
    print "sayMsg(" + msg + ")"
    return "say " + msg + " from " + socket.gethostbyname(socket.gethostname())
 
handler = HelloWorldHandler()
processor = MmtService.Processor(handler)
transport = TSocket.TServerSocket('127.0.0.1', 30303)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()
 
server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
 
print "Starting python server..."
server.serve()
print "done!"