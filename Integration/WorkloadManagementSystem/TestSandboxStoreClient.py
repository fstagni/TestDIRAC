""" This is a test of using SandboxStoreClient in the WMS

    In order to run this test we need the following DBs installed:
    - SandboxMetadataDB

    And the following services should also be on:
    - SandboxStore

    And a SandboxSE should be configured, something like:
      SandboxStore
      {
        LocalSE = FedericoSandboxSE
        Port = 9196
        BasePath = /home/toffo/Rumenta/
        Authorization
        {
          Default = authenticated
          FileTransfer
          {
            Default = all
          }
        }
      }

    A user proxy is also needed to submit,
    and the Framework/ProxyManager need to be running with a such user proxy already uploaded.
"""

import unittest

from DIRAC.Core.Base.Script import parseCommandLine
parseCommandLine()

from DIRAC import gLogger

from DIRAC.WorkloadManagementSystem.Client.SandboxStoreClient import SandboxStoreClient
from DIRAC.WorkloadManagementSystem.DB.SandboxMetadataDB import SandboxMetadataDB


class TestSSCTestCase( unittest.TestCase ):

  def setUp( self ):
    self.maxDiff = None

    gLogger.setLevel( 'VERBOSE' )

  def tearDown( self ):
    """
    """
    pass

class SSC( TestSSCTestCase ):

  def test_SSCChain( self ):
    """ full test of functionalities
    """
    ssc = SandboxStoreClient()
    smDB = SandboxMetadataDB()

    fileList = ['exe-script.py']
    res = ssc.uploadFilesAsSandbox( fileList )
    self.assert_( res['OK'] )
#     SEPFN = res['Value'].split( '|' )[1]
    res = ssc.uploadFilesAsSandboxForJob( fileList, 1, 'Input' )
    self.assert_( res['OK'] )
#     res = ssc.downloadSandboxForJob( 1, 'Input' ) #to run this would need the RSS on
#     self.assert_( res['OK'] )

    # only ones needing the DB
    res = smDB.getUnusedSandboxes()
    self.assert_( res['OK'] )
    # cleaning
#     smDB.deleteSandboxes( self, SBIdList )



if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase( TestSSCTestCase )
  suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( SSC ) )
  testResult = unittest.TextTestRunner( verbosity = 2 ).run( suite )
