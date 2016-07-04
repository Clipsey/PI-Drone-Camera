import pygame
import RPi.GPIO as GPIO
import socket
import struct

def stopPWM(rBackA, rFrontA, lBackA, lFrontA, camX, camY):
    rBackA.stop()
    rFrontA.stop()
    lBackA.stop()
    lFrontA.stop()
    camX.stop()
    camY.stop()

def exitProgram(sock):
    sock.close()
    GPIO.cleanup() 
    pygame.quit()
    exit()
    
def motorControl(axisx, axisy, rBackA, rFrontA, lBackA, lFrontA):
    #scaling speed forward
    if axisy > 0.30 and axisx < 0.30 and axisx > -0x30:
        lFrontA.ChangeDutyCycle(axisy * 100)
        lBackA.ChangeDutyCycle(axisy * 100)
        rFrontA.ChangeDutyCycle(axisy * 100)
        rBackA.ChangeDutyCycle(axisy * 100)
        leftSide = 0
        rightSide = 0
    #scaling speed backward
    elif axisy < -0.30 and axisx < 0.30 and axisx > -0x30:
        lFrontA.ChangeDutyCycle((1 + axisy) * 100)
        lBackA.ChangeDutyCycle((1 + axisy) * 100)
        rFrontA.ChangeDutyCycle((1 + axisy) * 100)
        rBackA.ChangeDutyCycle((1 + axisy) * 100)
        leftSide = 1
        rightSide = 1
    #scaling rotational speed right    
    elif axisx > 0.30 and axisy < 0.30 and axisy > -0x30:
        lFrontA.ChangeDutyCycle((1 - axisx)  * 100)
        lBackA.ChangeDutyCycle((1 - axisx) * 100)
        rFrontA.ChangeDutyCycle(axisx * 100)
        rBackA.ChangeDutyCycle(axisx * 100)
        leftSide = 1
        rightSide = 0
    #scaling rotational speed left
    elif axisx < -0.30 and axisy < 0.30 and axisy > -0x30:
        lFrontA.ChangeDutyCycle((-1 * axisx) * 100)
        lBackA.ChangeDutyCycle((-1 * axisx) * 100)
        rFrontA.ChangeDutyCycle((1 + axisx) * 100)
        rBackA.ChangeDutyCycle((1 + axisx) * 100)
        leftSide = 0
        rightSide = 1
    else:
        lFrontA.ChangeDutyCycle(0)
        lBackA.ChangeDutyCycle(0)
        rFrontA.ChangeDutyCycle(0)
        rBackA.ChangeDutyCycle(0)
        leftSide = 0
        rightSide = 0
        
    GPIO.output(16,leftSide)
    GPIO.output(32,leftSide)
    GPIO.output(13,rightSide)
    GPIO.output(31,rightSide)

def cameraControl(axisx, axisy, camX, camY, dutyx, dutyy, center):
    if center == True:
        dutyx = 7.5
        dutyy = 7.5
    elif center == False and axisx > 0.70:
        if dutyx < 10:
            dutyx += 0.1
    elif center == False and axisx < -0.70:
        if dutyx > 5:
            dutyx -= 0.1
    elif center == False and axisy > 0.70:
        if dutyy < 10:
            dutyy += 0.01
    elif center == False and axisy < -0.70:
        if dutyy > 5:
            dutyy -= 5;
         
    camX.ChangeDutyCycle(dutyx)
    camY.ChangeDutyCycle(dutyy)
    
    
    
def GPIOInit():
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(11,GPIO.OUT)
    GPIO.setup(13,GPIO.OUT)
    
    GPIO.setup(29,GPIO.OUT)
    GPIO.setup(31,GPIO.OUT)

    GPIO.setup(16,GPIO.OUT)
    GPIO.setup(18,GPIO.OUT)
    
    GPIO.setup(32,GPIO.OUT)
    GPIO.setup(38,GPIO.OUT)
    
    GPIO.setup(35,GPIO.OUT)
    GPIO.setup(37,GPIO.OUT)
    
def UDPServerInit(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as msg:
        print ('Socket Create failed')
        print(msg)
        exitProgram(sock)
        
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        sock.bind((host,port))
    except socket.error as msg:
        print ('Bind failed')
        print(msg)
        exitProgram(sock)
    
    return sock
    
def testConnection(sock):
    try:
        print('Waiting for connection...')
        data = sock.recvfrom(1024)
        message = data[0].decode('UTF-8')
        address = data[1][0] + ":" + str(data[1][1])
        print('Signal from: ' + address)
        print('Signal: ' + message)
        print('Signal Received, Connection Successful')
    except KeyboardInterrupt:
        stopPWM(rBackA, rFrontA, lBackA, lFrontA, camX, camY)
        exitProgram(sock)
        

GPIOInit()    
rBackA = GPIO.PWM(11,50)
rBackA.start(0)
rFrontA = GPIO.PWM(29,50)
rFrontA.start(0)
lBackA = GPIO.PWM(18,50)
lBackA.start(0)
lFrontA = GPIO.PWM(38,50) 
lFrontA.start(0)

camX = GPIO.PWM(35,50)
dutyx = 7.5
camX.start(dutyx)
camY = GPIO.PWM(37,50)
dutyy = 7.5
camY.start(dutyy)
        
pygame.init()

#SERVERHOST = socket.gethostbyname(socket.gethostname())
SERVERHOST = ''
SERVERPORT = 1881
sock = UDPServerInit(SERVERHOST, SERVERPORT)
print("Remote Server is active")
print('Host Address: ', SERVERHOST)
print('Port Number: ', SERVERPORT)

unpacker = struct.Struct('f f f f ? ?')

testConnection(sock)

done = False
while done==False:
    try:
        packet, addr = sock.recvfrom(unpacker.size)
        axis_x, axis_y, axis_rx, axis_ry, center, status = unpacker.unpack(packet)
        motorControl(axis_x, axis_y, rBackA, rFrontA, lBackA, lFrontA)
        cameraControl(axis_rx, axis_ry, camX, camY, dutyx, dutyy, center)
        if status == True:
            done = True
            
    except KeyboardInterrupt:
        stopPWM(rBackA, rFrontA, lBackA, lFrontA, camX, camY)
        exitProgram(sock)
    
print("End signal received, exiting")
stopPWM(rBackA, rFrontA, lBackA, lFrontA, camX, camY)
exitProgram(sock)