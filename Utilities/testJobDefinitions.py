""" Collection of user jobs for testing purposes
"""

from TestDIRAC.Utilities.utils import find_all




tier1s = ['LCG.CERN.ch', 'LCG.CNAF.it', 'LCG.GRIDKA.de', 'LCG.IN2P3.fr', 'LCG.NIKHEF.nl',
          'LCG.PIC.es', 'LCG.RAL.uk', 'LCG.SARA.nl', 'LCG.RRCKI.ru']

# Common functions

def getJob():
  from DIRAC.Interfaces.API.Job import Job
  return Job()

def getDIRAC():
  from DIRAC.Interfaces.API.Dirac import Dirac
  return Dirac()

def baseToAllJobs( jName ):

  print "**********************************************************************************************************"
  print "\n Submitting job ", jName

  J = getJob()
  J.setName( jName )
  J.setCPUTime( 17800 )
  return J


def endOfAllJobs( J ):
  result = getDIRAC().submit( J )
  print "Job submission result:", result
  if result['OK']:
    jobID = int( result['Value'] )
    print "Submitted with job ID:", jobID

  return result

  print "**********************************************************************************************************"




# List of jobs

def helloWorld():

  J = baseToAllJobs( 'helloWorld' )
  J.setInputSandbox( [find_all( 'exe-script.py', '.', 'GridTestSubmission' )[0]] )
  J.setExecutable( "exe-script.py", "", "helloWorld.log" )
  return endOfAllJobs( J )

