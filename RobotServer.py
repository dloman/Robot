#!/usr/bin/python
from glob import glob
import serial
import web

urls = ('/(.*)', 'Drive')
app = web.application(urls, globals())

###############################################################################
###############################################################################
class Drive:
  ##############################################################################
  def __init__(self):
    self.ConnectToSerial()

  ##############################################################################
  def POST(self, *args,**kwargs):
    Data = web.input()
    self.WriteMotors(Data['motor1'], Data['motor2'], Data['motor3'])

  ##############################################################################
  def ConnectToSerial(self):
    for ttyName in glob('/dev/ttyACM*'):
      try:
       print 'trying motor controller on', ttyName
       self.mSerial = serial.Serial(ttyName, 115200, timeout=.1)
       print 'Connected on to motor controller on', ttyName
       return
      except:
        pass
    else:
      print 'Serial Connection could not be established'
      return
      exit()

  ##############################################################################
  def WriteMotors(self, motor1, motor2, motor3):
    try:
      print '!' + motor1 + ',' + motor2 + ',' + motor3 + '\n'
      self.mSerial.write('!' + str(motor1) + ',' + str(motor2) + ',' + str(motor3) + '\n')
      self.mSerial.flush()
    except:
      self.ConnectToSerial()

################################################################################
################################################################################
if __name__ == "__main__":
  web.config.debug = False
  try:
    app.run()
  except:
    print 'webpy didnt work'
    exit()


