""" This is a test of the chain
    ReqClient -> ReqManagerHandler -> ReqDB

    It supposes that the DB is present, and that the service is running
"""

from DIRAC.Core.Base.Script import parseCommandLine
parseCommandLine()

import unittest

from DIRAC import gLogger

from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.File import File
from DIRAC.RequestManagementSystem.Client.ReqClient import ReqClient

from DIRAC.RequestManagementSystem.DB.RequestDB import RequestDB

import time

class ReqClientTestCase( unittest.TestCase ):
  """
  .. class:: ReqClientTestCase

  """

  def setUp( self ):
    """ test case set up """

    gLogger.setLevel( 'NOTICE' )

    self.file = File()
    self.file.LFN = "/lhcb/user/c/cibak/testFile"
    self.file.Checksum = "123456"
    self.file.ChecksumType = "ADLER32"

    self.file2 = File()
    self.file2.LFN = "/lhcb/user/f/fstagni/testFile"
    self.file2.Checksum = "654321"
    self.file2.ChecksumType = "ADLER32"

    self.operation = Operation()
    self.operation.Type = "ReplicateAndRegister"
    self.operation.TargetSE = "CERN-USER"
    self.operation.addFile( self.file )
    self.operation.addFile( self.file2 )

    self.request = Request()
    self.request.RequestName = "RequestManagerHandlerTests"
    self.request.OwnerDN = "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cibak/CN=605919/CN=Krzysztof Ciba"
    self.request.OwnerGroup = "dirac_user"
    self.request.JobID = 123
    self.request.addOperation( self.operation )

    # # JSON representation of a whole request
    self.jsonStr = self.request.toJSON()['Value']
    # # request client
    self.requestClient = ReqClient()

    self.stressRequests = 1000
    self.bulkRequest = 1000


  def tearDown( self ):
    """ clean up """
    del self.request
    del self.operation
    del self.file
    del self.jsonStr

class ReqDB( ReqClientTestCase ):

  def test_db( self ):

    """ table description """
    tableDict = RequestDB.getTableMeta()
    self.assertEqual( "Request" in tableDict, True )
    self.assertEqual( "Operation" in tableDict, True )
    self.assertEqual( "File" in tableDict, True )


    # # empty DB at that stage
    ret = RequestDB().getDBSummary()
    self.assertEqual( ret,
                      { 'OK': True,
                        'Value': { 'Operation': {}, 'Request': {}, 'File': {} } } )


class ReqClientMix( ReqClientTestCase ):

  def test_fullChain( self ):
    put = self.requestClient.putRequest( self.request )
    self.assert_( put['OK'] )

    # # summary
    ret = RequestDB().getDBSummary()
    self.assertEqual( ret,
                      { 'OK': True,
                        'Value': { 'Operation': { 'ReplicateAndRegister': { 'Waiting': 1L } },
                                   'Request': { 'Waiting': 1L },
                                   'File': { 'Waiting': 2L} } } )

    get = self.requestClient.getRequest( self.request.RequestName )
    self.assert_( get['OK'] )
    self.assertEqual( isinstance( get['Value'], Request ), True )
    # # summary - the request became "Assigned"
    res = RequestDB().getDBSummary()
    self.assertEqual( res,
                      { 'OK': True,
                        'Value': { 'Operation': { 'ReplicateAndRegister': { 'Waiting': 1L } },
                                   'Request': { 'Assigned': 1L },
                                   'File': { 'Waiting': 2L} } } )


    res = self.requestClient.getRequestInfo( self.request.RequestName )
    self.assert_( res['OK'] )
    res = self.requestClient.getRequestName( res['Value'][0] )
    self.assert_( res['OK'] )
    self.assertEqual( res['Value'], self.request.RequestName )

    res = self.requestClient.getRequestFileStatus( self.request.RequestName, self.file.LFN )
    self.assert_( res['OK'] )

    res = self.requestClient.getRequestFileStatus( self.request.RequestName, [self.file.LFN] )
    self.assert_( res['OK'] )

    res = self.requestClient.getDigest( self.request.RequestName )
    self.assert_( res['OK'] )

    res = self.requestClient.getRequestNamesForJobs( [123] )
    self.assert_( res['OK'] )
    self.assertEqual( res['Value'], {'Successful': {123L:self.request.RequestName}, 'Failed': {}} )

    res = self.requestClient.getRequestNamesList()
    self.assert_( res['OK'] )

    res = self.requestClient.readRequestsForJobs( [123] )
    self.assert_( res['OK'] )
    self.assert_( isinstance( res['Value']['Successful'][123], Request ) )

    # Adding new request
    request2 = Request()
    request2.RequestName = "RequestManagerHandlerTests-2"
    request2.OwnerDN = "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cibak/CN=605919/CN=Krzysztof Ciba"
    request2.OwnerGroup = "dirac_user"
    request2.JobID = 456
    request2.addOperation( self.operation )

    # # update
    res = self.requestClient.putRequest( request2 )
    self.assert_( res['OK'] )

    # # get summary again
    ret = RequestDB().getDBSummary()
    self.assertEqual( ret,
                      { 'OK': True,
                        'Value': { 'Operation': { 'ReplicateAndRegister': {'Waiting': 2L } },
                                   'Request': { 'Waiting': 1L, 'Assigned': 1L },
                                   'File': { 'Waiting': 4L} } } )


    delete = self.requestClient.deleteRequest( self.request.RequestName )
    self.assert_( delete['OK'] )
    delete = self.requestClient.deleteRequest( request2.RequestName )
    self.assert_( delete['OK'] )

    # # should be empty now
    ret = RequestDB().getDBSummary()
    self.assertEqual( ret,
                      { 'OK': True,
                        'Value': { 'Operation': {}, 'Request': {}, 'File': {} } } )



# FIXME: add the following:


  def test04Stress( self ):
    """ stress test """

    db = RequestDB()


    for i in range( self.stressRequests ):
      request = Request( { "RequestName": "test-%d" % i } )
      op = Operation( { "Type": "RemoveReplica", "TargetSE": "CERN-USER" } )
      op += File( { "LFN": "/lhcb/user/c/cibak/foo" } )
      request += op
      put = db.putRequest( request )
      self.assertEqual( put["OK"], True, "put failed" )

    startTime = time.time()

    for i in range( self.stressRequests ):
      get = db.getRequest( "test-%s" % i, True )
      if "Message" in get:
        print get["Message"]
      self.assertEqual( get["OK"], True, "get failed" )

    endTime = time.time()

    print "getRequest duration %s " % ( endTime - startTime )

    for i in range( self.stressRequests ):
      delete = db.deleteRequest( "test-%s" % i )
      self.assertEqual( delete["OK"], True, "delete failed" )


  def test04StressBulk( self ):
    """ stress test bulk """

    db = RequestDB()

    for i in range( self.stressRequests ):
      request = Request( { "RequestName": "test-%d" % i } )
      op = Operation( { "Type": "RemoveReplica", "TargetSE": "CERN-USER" } )
      op += File( { "LFN": "/lhcb/user/c/cibak/foo" } )
      request += op
      put = db.putRequest( request )
      self.assertEqual( put["OK"], True )

    loops = self.stressRequests // self.bulkRequest + ( 1 if ( self.stressRequests % self.bulkRequest ) else 0 )
    totalSuccessful = 0

    startTime = time.time()

    for i in range( loops ):
      get = db.getBulkRequests( self.bulkRequest, True )
      if "Message" in get:
        print get["Message"]
      self.assertEqual( get["OK"], True, "get failed" )

      totalSuccessful += len( get["Value"] )

    endTime = time.time()

    print "getRequests duration %s " % ( endTime - startTime )

    self.assertEqual( totalSuccessful, self.stressRequests, "Did not retrieve all the requests: %s instead of %s" % ( totalSuccessful, self.stressRequests ) )

    for i in range( self.stressRequests ):
      delete = db.deleteRequest( "test-%s" % i )
      self.assertEqual( delete["OK"], True, "delete failed" )
#
#
#  def test05Scheduled( self ):
#    """ scheduled request r/w """
#
#    db = RequestDB()
#
#    req = Request( {"RequestName": "FTSTest"} )
#    op = Operation( { "Type": "ReplicateAndRegister", "TargetSE": "CERN-USER"} )
#    op += File( {"LFN": "/a/b/c", "Status": "Scheduled", "Checksum": "123456", "ChecksumType": "ADLER32" } )
#    req += op
#
#    put = db.putRequest( req )
#    self.assertEqual( put["OK"], True, "putRequest failed" )
#
#    peek = db.peekRequest( req.RequestName )
#    self.assertEqual( peek["OK"], True, "peek failed " )
#
#    peek = peek["Value"]
#    for op in peek:
#      opId = op.OperationID
#
#    getFTS = db.getScheduledRequest( opId )
#    self.assertEqual( getFTS["OK"], True, "getScheduled failed" )
#    self.assertEqual( getFTS["Value"].RequestName, "FTSTest", "wrong request selected" )
#
#
#  def test06Dirty( self ):
#    """ dirty records """
#    db = RequestDB()
#
#    r = Request()
#    r.RequestName = "dirty"
#
#    op1 = Operation( { "Type": "ReplicateAndRegister", "TargetSE": "CERN-USER"} )
#    op1 += File( {"LFN": "/a/b/c/1", "Status": "Scheduled", "Checksum": "123456", "ChecksumType": "ADLER32" } )
#
#    op2 = Operation( { "Type": "ReplicateAndRegister", "TargetSE": "CERN-USER"} )
#    op2 += File( {"LFN": "/a/b/c/2", "Status": "Scheduled", "Checksum": "123456", "ChecksumType": "ADLER32" } )
#
#    op3 = Operation( { "Type": "ReplicateAndRegister", "TargetSE": "CERN-USER"} )
#    op3 += File( {"LFN": "/a/b/c/3", "Status": "Scheduled", "Checksum": "123456", "ChecksumType": "ADLER32" } )
#
#    r += op1
#    r += op2
#    r += op3
#
#    put = db.putRequest( r )
#    self.assertEqual( put["OK"], True, "1. putRequest failed: %s" % put.get( "Message", "" ) )
#
#
#    r = db.getRequest( "dirty" )
#    self.assertEqual( r["OK"], True, "1. getRequest failed: %s" % r.get( "Message", "" ) )
#    r = r["Value"]
#
#    del r[0]
#    self.assertEqual( len( r ), 2, "1. len wrong" )
#
#    put = db.putRequest( r )
#    self.assertEqual( put["OK"], True, "2. putRequest failed: %s" % put.get( "Message", "" ) )
#
#    r = db.getRequest( "dirty" )
#    self.assertEqual( r["OK"], True, "2. getRequest failed: %s" % r.get( "Message", "" ) )
#
#    r = r["Value"]
#    self.assertEqual( len( r ), 2, "2. len wrong" )
#
#    op4 = Operation( { "Type": "ReplicateAndRegister", "TargetSE": "CERN-USER"} )
#    op4 += File( {"LFN": "/a/b/c/4", "Status": "Scheduled", "Checksum": "123456", "ChecksumType": "ADLER32" } )
#
#    r[0] = op4
#    put = db.putRequest( r )
#    self.assertEqual( put["OK"], True, "3. putRequest failed: %s" % put.get( "Message", "" ) )
#
#    r = db.getRequest( "dirty" )
#    self.assertEqual( r["OK"], True, "3. getRequest failed: %s" % r.get( "Message", "" ) )
#    r = r["Value"]
#
#    self.assertEqual( len( r ), 2, "3. len wrong" )



if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase( ReqClientTestCase )
  suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( ReqDB ) )
  suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( ReqClientMix ) )
  testResult = unittest.TextTestRunner( verbosity = 2 ).run( suite )
