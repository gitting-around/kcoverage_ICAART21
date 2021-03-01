#!/usr/bin/env python
 
import sys

sys.path.append('..')
 
from SharedDefinitions9 import PlannerService
from SharedDefinitions9 import MmtService
from SharedDefinitions9.ttypes import *
from SharedDefinitions9.constants import *
 
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
 
try:
  # Make socket
  transport = TSocket.TSocket('127.0.0.1', 30303)
 
  # Buffering is critical. Raw sockets are very slow
  transport = TTransport.TBufferedTransport(transport)
 
  # Wrap in a protocol
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
 
  # Create a client to use the protocol encoder
  client = PlannerService.Client(protocol)
 
  # Connect!
  transport.open()
 
  client.ping()
  print "ping()"
 
  transport.close()
 
except Thrift.TException, tx:
  print "%s" % (tx.message)