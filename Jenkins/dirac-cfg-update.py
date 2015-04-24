#!/usr/bin/env python
""" update local cfg
"""

from DIRAC.Core.Base import Script
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgFile]' % Script.scriptName] ) )

Script.registerSwitch( 'F:', 'file=', "set the cfg file to update." )

Script.parseCommandLine()
args = Script.getPositionalArgs()

cFile = ''
for unprocSw in Script.getUnprocessedSwitches():
  if unprocSw[0] in ( "F", "file" ):
    cFile = unprocSw[1]

import os

from DIRAC.Core.Utilities.CFG import CFG

localCfg = CFG()
if cFile:
  localCfg.loadFromFile( cFile )
else:
  localCfg.loadFromFile( './etc/dirac.cfg' )

if not localCfg.isSection( '/LocalSite' ):
  localCfg.createNewSection( '/LocalSite' )
localCfg.setOption( '/LocalSite/CPUTimeLeft', 5000 )
localCfg.setOption( '/DIRAC/Security/UseServerCertificate', False )
localCfg.writeToFile( localConfigFile )
