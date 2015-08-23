#!/usr/bin/python
"""RobotController.

Usage:
    RobotController.py [options]...

Options:
    -h -? --help                     Show this screen.
    -v --version                     Show version.
    -s STARTSPEED               Sets the robot's starting speed. [default: 35]
    -m MAXSPEED                 Sets the robot's starting speed. [default: 255]
    -a ACCELERATION             Sets the robot's acceleration. [default: 10]
    -r ROTATIONRATE             Sets the robot's rotation rate. [default: 55]
    -t --tow-mode                    Uses the "tow mode" presets.
    -d --danger-zone                 Uses the "danger zone presets.
"""
import pygame
from pygame.locals import *
from glob import glob
import time
import serial
import os
import sys
from math import pi
from docopt import docopt

################################################################################
################################################################################
class Robot(object):
  ##############################################################################
  def __init__(self, Args):
    pygame.init()
    self.mSpeed = 0
    self.mStartingSpeed = int(inputArguments['-s'][0])
    self.mMaxSpeed = int(inputArguments['-m'][0])
    self.mAcceleration = int(inputArguments['-a'][0])
    self.mTurnSpeed = int(inputArguments['-r'][0])
    if inputArguments['--tow-mode']:
      self.mStartingSpeed = 35
      self.mAcceleration = 5
      self.mTurnSpeed = 45
    elif inputArguments['--danger-zone']:
      self.mStartingSpeed = 55
      self.mAcceleration = 15
      self.mTurnSpeed = 150
    self.mDisplay = pygame.display.set_mode((100,100))
    pygame.display.update()
    #self.ConnectToSerial()

  ##############################################################################
  def ConnectToSerial(self):

    for ttyName in glob('/dev/ttyACM*'):
      try:
       self.mSerial = serial.Serial(ttyName, 115200, timeout=.1)
       print 'Connected on to motor controller on', ttyName
       return
      except:
        pass
    else:
      print 'Serial Connection could not be established'
      exit()

  ##############################################################################
  def JoystickMove(self, LeftStick, RightStick):
    if LeftStick != 0.0 or RightStick != 0.0:
      print 'LeftStick = ', LeftStick, 'RightStick =', RightStick
    motor1 = 0; motor2 = 0; motor3 = 0;
    motor2 += int(LeftStick * -self.mMaxSpeed)
    motor3 += int(LeftStick * self.mMaxSpeed)
    motor1 += int(self.mTurnSpeed * (RightStick))
    motor2 += int(self.mTurnSpeed * (RightStick))
    motor3 += int(self.mTurnSpeed * (RightStick))
    self.WriteMotors(motor1, motor2, motor3)


  ##############################################################################
  def Move(self, Keys):
    motor1 = 0; motor2 = 0; motor3 = 0;
    if any(Keys):
      if Keys[K_ESCAPE] or Keys[113]:
        pygame.quit()
        print 'quiting'
        exit()
      if Keys[115] or Keys[K_DOWN]: #s
        motor2 = -self.mSpeed
        motor3 = self.mSpeed
      if Keys[119] or Keys[K_UP]: #w
        motor2 = self.mSpeed
        motor3 = -self.mSpeed
      if Keys[97]:  #a
        motor1 = -self.mSpeed
        motor2 = self.mSpeed/2
        motor3 = self.mSpeed/2
      if Keys[100]:  #d
        motor1 = self.mSpeed
        motor2 = -self.mSpeed/2
        motor3 = -self.mSpeed/2
      if Keys[K_LEFT]:
        motor1 -= self.mTurnSpeed
        motor2 -= self.mTurnSpeed
        motor3 -= self.mTurnSpeed
      if Keys[K_RIGHT]:
        motor1 += self.mTurnSpeed
        motor2 += self.mTurnSpeed
        motor3 += self.mTurnSpeed
      if self.mSpeed < self.mMaxSpeed:
        self.mSpeed += self.mAcceleration
      if self.mAcceleration <= self.mSpeed < self.mStartingSpeed:
        self.mSpeed = self.mStartingSpeed
      if self.mSpeed % 2:
        self.mSpeed += 1
      self.WriteMotors(motor1, motor2, motor3)
    else:
      self.mSpeed = 0
    time.sleep(.05)

  ##############################################################################
  ##############################################################################
  def WriteMotors(self, motor1, motor2, motor3):
    print '!'+str(motor1)+','+str(motor2)+','+str(motor3)+'\n'
    try:
      self.mSerial.write('!'+str(motor1)+','+str(motor2)+','+str(motor3)+'\n')
      self.mSerial.flush()
    except:
      #self.ConnectToSerial()
      pass

################################################################################
################################################################################
if __name__ == "__main__":
  inputArguments = docopt(__doc__, version =0.1)
  clock = pygame.time.Clock()
  robot = Robot(inputArguments)
  pygame.joystick.init()
  joystick = pygame.joystick.Joystick(0)
  joystick.init()

  while True:
    try:
      clock.tick(60)
      Keys = pygame.key.get_pressed()
      robot.Move(Keys)
      LeftStick = joystick.get_axis(1)
      RightStick = joystick.get_axis(3)
      robot.JoystickMove(LeftStick, RightStick)
      pygame.event.pump() # process event queue

    except KeyboardInterrupt:
      pygame.quit()
      exit()

