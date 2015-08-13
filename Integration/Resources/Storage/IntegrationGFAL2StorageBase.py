"""
This tests the new plugins for rel-v6r13: GFAL2_SRM2Storage and GFAL2_XROOTStorage.

Plugins:

To run the test following plugins are needed:

gfal2-2.8.1-1
gfal2-plugin-xrootd-0.2.2-2
gfal2-python-1.6.0-1
Storage element:

Change self.storageName within the basicTest class to the name of the storageElement you wish to run this test against.
This storage element needs to be supporting two access protocols, using the protocolName GFAL2_SRM2 and GFAL2_XROOT
respectively. If you want to test only either SRM2 or XROOT remove the other testsuite in the unittest.

"""


from DIRAC.Core.Base.Script import parseCommandLine
parseCommandLine()

import unittest

from DIRAC import gLogger
from DIRAC.Resources.Storage.StorageElement import StorageElement

class basicTest( unittest.TestCase ):

  def setUp( self ):
    gLogger.setLevel( 'DEBUG' )

    self.storageName = 'CERN-GFAL2'
    self.tbt = None


  def testWorkflow( self ):
    putDir = {'/lhcb/user/p/pgloor/Workflow/FolderA' : '/home/phi/dev/UnitTests/FolderA' ,
              '/lhcb/user/p/pgloor/Workflow/FolderB' : '/home/phi/dev/UnitTests/FolderB' }

    createDir = ['/lhcb/user/p/pgloor/Workflow/FolderA/FolderAA' ,
                 '/lhcb/user/p/pgloor/Workflow/FolderA/FolderABA',
                 '/lhcb/user/p/pgloor/Workflow/FolderA/FolderAAB' ]

    putFile = {'/lhcb/user/p/pgloor/Workflow/FolderA/File1' : '/home/phi/dev/UnitTests/File1',
               '/lhcb/user/p/pgloor/Workflow/FolderAA/File1': '/home/phi/dev/UnitTest/File1',
               '/lhcb/user/p/pgloor/Workflow/FolderBB/File2': '/home/phi/dev/UnitTest/File2',
               '/lhcb/user/p/pgloor/Workflow/FolderB/File2' : '/home/phi/dev/UnitTests/File2',
               '/lhcb/user/p/pgloor/Workflow/File3' : '/home/phi/dev/UnitTests/File3' }

    isFile = ['/lhcb/user/p/pgloor/Workflow/FolderA/File1']

    listDir = ['/lhcb/user/p/pgloor/Workflow', \
               '/lhcb/user/p/pgloor/Workflow/FolderA', \
               '/lhcb/user/p/pgloor/Workflow/FolderB']

    getDir = [ '/lhcb/user/p/pgloor/Workflow/FolderA', \
           '/lhcb/user/p/pgloor/Workflow/FolderB']

    removeFile = ['/lhcb/user/p/pgloor/Workflow/FolderA/File1']
    rmdir = ['/lhcb/user/p/pgloor/Workflow']

    ########## uploading directory #############
    res = self.tbt.putDirectory( putDir )
    self.assertEqual( res['OK'], True )
    res = self.tbt.listDirectory( listDir )
    self.assertEqual( any('/lhcb/user/p/pgloor/Workflow/FolderA/FileA' in dictKey for dictKey in \
                  res['Value']['Successful']['/lhcb/user/p/pgloor/Workflow/FolderA']['Files'].keys() ), True )
    self.assertEqual( any( '/lhcb/user/p/pgloor/Workflow/FolderB/FileB' in dictKey for dictKey in \
                      res['Value']['Successful']['/lhcb/user/p/pgloor/Workflow/FolderB']['Files'].keys() ), True )

    ########## createDir #############
    res = self.tbt.createDirectory( createDir )
    self.assertEqual( res['OK'], True )
    res = res['Value']
    self.assertEqual( res['Successful'][createDir[0]], True )
    self.assertEqual( res['Successful'][createDir[1]], True )
    self.assertEqual( res['Successful'][createDir[2]], True )

    ######## putFile ########
    res = self.tbt.putFile( putFile )
    self.assertEqual( res['OK'], True )

    res = self.tbt.isFile( isFile )
    self.assertEqual( res['OK'], True )
    self.assertEqual( res['Value']['Successful'][isFile[0]], True )

    ####### getDirectory ######
    res = self.tbt.getDirectory( getDir, '/home/phi/dev/UnitTests/getDir' )
    self.assertEqual( res['OK'], True )
    res = res['Value']
    self.assertEqual( any( getDir[0] in dictKey for dictKey in res['Successful'] ), True )
    self.assertEqual( any( getDir[1] in dictKey for dictKey in res['Successful'] ), True )

    ###### removeFile ##########
    res = self.tbt.removeFile( removeFile )
    self.assertEqual( res['OK'], True )
    res = self.tbt.exists( removeFile )
    self.assertEqual( res['OK'], True )
    self.assertEqual( res['Value']['Successful'][removeFile[0]], False )

    ########### removing directory  ###########
    res = self.tbt.removeDirectory( rmdir, True )
    res = self.tbt.exists( rmdir )
    self.assertEqual( res['OK'], True )
    self.assertEqual( res['Value']['Successful'][rmdir[0]], False )

class SRM2V2Test( basicTest ):

  def setUp( self ):
    basicTest.setUp( self )
    self.tbt = StorageElement( self.storageName, protocols = 'GFAL2_SRM2' )


class XROOTTest( basicTest ):

  def setUp( self ):
    basicTest.setUp( self )
    self.tbt = StorageElement( self.storageName, protocols = 'GFAL2_XROOT' )


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase( SRM2V2Test )
  suite.addTest( unittest.defaultTestLoader.loadTestsFromTestCase( XROOTTest ) )
  unittest.TextTestRunner( verbosity = 2 ).run( suite )
