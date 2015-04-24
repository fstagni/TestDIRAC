#!/usr/bin/env python
""" update local cfg
"""

from DIRAC.Core.Base import Script
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgFile] cfgFile' % Script.scriptName] ) )
Script.parseCommandLine()
args = Script.getPositionalArgs()


import os

from DIRAC.Core.Utilities.CFG import CFG

localCfg = CFG()
if len( args ) == 1:
  localConfigFile = os.path.join( '.', args[0] )
  localCfg.loadFromFile( localConfigFile )
else:
  localCfg.loadFromFile( './etc/dirac.cfg' )

if not localCfg.isSection( '/LocalSite' ):
  localCfg.createNewSection( '/LocalSite' )
localCfg.setOption( '/LocalSite/CPUTimeLeft', 5000 )
localCfg.setOption( '/DIRAC/Security/UseServerCertificate', False )
localCfg.writeToFile( localConfigFile )
