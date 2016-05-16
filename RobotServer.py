#!/usr/bin/python
from glob import glob
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import serial

###############################################################################
###############################################################################
class Robot(Protocol):
  def __init__(self):
    pass
    self.ConnectToSerial()

  ##############################################################################
  def ConnectToSerial(self):
    for ttyName in glob('/dev/ttyACM*'):
      try:
       print 'trying motor controller on', ttyName
       self.mSerial = serial.Serial(ttyName, 115200, timeout=.1)
       print 'Connected on to motor controller on', ttyName
       return
      except:
        self.mSerial = None
        pass

  ##############################################################################
  def WriteMotors(self, motor1, motor2, motor3):
    try:
      if self.mSerial:
        self.mSerial.write('!' + motor1 + ',' + motor2 + ',' + motor3 + '\n')
        self.mSerial.flush()
      else:
        self.ConnectToSerial()
    except:
      self.ConnectToSerial()

  ##############################################################################
  def connectionMade(self):
    pass

  ##############################################################################
  def connectionLost(self, reason):
    pass

  ##############################################################################
  def dataReceived(self, data):
    data = data.strip('\n')
    data = data.split(',')
    if len(data) == 3:
      self.WriteMotors(data[0], data[1], data[2])

################################################################################
################################################################################
if __name__ == "__main__":
  factory = Factory()
  factory.protocol = Robot
  reactor.listenTCP(8080, factory)
  reactor.run()

