#!/usr/bin/env python
""" update local cfg
"""

from DIRAC.Core.Base import Script

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgFile] ... DB ...' % Script.scriptName] ) )

Script.parseCommandLine()

args = Script.getPositionalArgs()
setupName = args[0]

import os

# Where to store outputs
if not os.path.isdir( '%s/sandboxes' % setupName ):
  os.makedirs( '%s/sandboxes' % setupName )

# now updating the CS

from DIRAC.ConfigurationSystem.Client.CSAPI import CSAPI
csAPI = CSAPI()

csAPI.setOption( 'Systems/WorkloadManagement/Production/Services/SandboxStore/BasePath', '%s/sandboxes' % setupName )
csAPI.setOption( 'Systems/WorkloadManagement/Production/Services/SandboxStore/LogLevel', 'DEBUG' )

# Now setting a SandboxSE as the following:
#     ProductionSandboxSE
#     {
#       BackendType = DISET
#       AccessProtocol.1
#       {
#         Host = localhost
#         Port = 9196
#         ProtocolName = DIP
#         Protocol = dips
#         Path = /scratch/workspace/%s/sandboxes % setupName
#         Access = remote
#         SpaceToken =
#         WSUrl =
#       }
#     }
res = csAPI.createSection( 'Resources/StorageElements/' )
if not res['OK']:
  print res['Message']
  exit( 1 )

res = csAPI.createSection( 'Resources/StorageElements/ProductionSandboxSE' )
if not res['OK']:
  print res['Message']
  exit( 1 )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/BackendType', 'DISET' )

res = csAPI.createSection( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1' )
if not res['OK']:
  print res['Message']
  exit( 1 )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1/Host', 'localhost' )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1/Port', '9196' )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1/ProtocolName', 'DIP' )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1/Path', '%s/sandboxes' % setupName )
csAPI.setOption( 'Resources/StorageElements/ProductionSandboxSE/AccessProtocol.1/Access', 'remote' )

csAPI.commit()
