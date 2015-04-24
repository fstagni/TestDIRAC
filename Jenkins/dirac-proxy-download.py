#!/usr/bin/env python
""" Get a proxy from the proxy manager
"""

from DIRAC.Core.Base import Script

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgFile] UserName Role' % Script.scriptName,
                                     'Arguments:',
                                     '  UserName: User DN',
                                     '  Role: User role'] ) )
Script.parseCommandLine()
args = Script.getPositionalArgs()

if len( args ) < 2:
  Script.showHelp()
  exit( -1 )

import os
uid = os.getuid()
from DIRAC.FrameworkSystem.Client.ProxyManagerClient        import gProxyManager

res = gProxyManager.downloadProxyToFile( args[0], args[1],
                                         limited = False, requiredTimeLeft = 1200,
                                         cacheTime = 43200, filePath = '/tmp/x509up_u%s' % uid, proxyToConnect = False,
                                         token = False )

if not res['OK']:
  print "Error downloading proxy", res['Message']
  exit( 1 )
