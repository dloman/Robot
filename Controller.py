#!/usr/bin/python
"""Controller.

Usage:
    Controller.py [options]...

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
from docopt import docopt
from math import pi
import os
import pygame
from pygame.locals import *
import socket
import subprocess
import requests
import time

################################################################################
################################################################################
class Robot(object):
  ##############################################################################
  def __init__(self, Args):
    self.mSpeed = 0
    self.mStartingSpeed = int(inputArguments['-s'][0])
    self.mMaxSpeed = int(inputArguments['-m'][0])
    self.mAcceleration = int(inputArguments['-a'][0])
    self.mTurnSpeed = int(inputArguments['-r'][0])
    self.mLastUpdateTime = time.time()
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

    self.setupSocket()

  ##############################################################################
  def setupSocket(self):
    try:
      self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.mSocket.connect(('localhost', 8080))
    except:
      time.sleep(1)
      self.mSocket = None

  ##############################################################################
  def JoystickMove(self, LeftStick, RightStick):
    if LeftStick != 0.0 or RightStick != 0.0:
      self.mLastUpdateTime = time.time()
    motor1 = 0; motor2 = 0; motor3 = 0;
    motor2 += int(LeftStick * -self.mMaxSpeed)
    motor3 += int(LeftStick * self.mMaxSpeed)
    motor1 += int(self.mTurnSpeed * (RightStick))
    motor2 += int(self.mTurnSpeed * (RightStick))
    motor3 += int(self.mTurnSpeed * (RightStick))
    self.WriteMotors(motor1, motor2, motor3)
    if time.time() - self.mLastUpdateTime > 100:
      pygame.joystick.quit()
      gJoystick = None



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
  def WriteMotors(self, motor1, motor2, motor3):
    if self.mSocket:
      self.mSocket.send(str(motor1) + ',' + str(motor2) + ',' + str(motor3)+'\n')
    else:
      self.setupSocket()

  ##############################################################################
  def CloseSocket(self):
    if self.Socket:
      self.mSocket.close()

################################################################################
def getJoystick():
  try:
    if subprocess.check_output(['hidd', '--show']) == '':
      subprocess.check_call(['hidd', '--connect', 'B8:5A:F7:C1:7A:3D'])

    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick
  except Exception as e:
    pygame.joystick.quit()
    return None

################################################################################
################################################################################
def bluetoothSetup():
  os.system('rfkill unblock bluetooth')
  os.system('hciconfig hci0 up')

################################################################################
################################################################################
if __name__ == "__main__":
  inputArguments = docopt(__doc__, version =0.1)
  bluetoothSetup()
  clock = pygame.time.Clock()
  robot = Robot(inputArguments)
  joystick = None
  pygame.init()

  while True:
    try:
      clock.tick(60)
      Keys = pygame.key.get_pressed()
      robot.Move(Keys)
      if joystick:
        LeftStick = joystick.get_axis(1)
        RightStick = joystick.get_axis(3)
        joystick = robot.JoystickMove(LeftStick, RightStick)
        if subprocess.check_output(['hidd', '--show']) == '':
          print 'reconnecting'
          joystick = getJoystick()
      else:
        joystick = getJoystick()
      pygame.event.pump() # process event queue

    except KeyboardInterrupt:
      robot.CloseSocket()
      pygame.quit()
      exit()


