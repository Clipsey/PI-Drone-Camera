import pygame
import socket
import struct
import serial
import time

def joystickSetup():
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick

def UDPServerInit(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as msg:
        print ('Socket Create failed')
        print(msg)
        sock.close()
        pygame.quit()
        exit()
        
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        sock.bind((host,port))
    except socket.error as msg:
        print ('Bind failed')
        print(msg)
        sock.close() 
        pygame.quit()
        exit()
    
    return sock


class Drone_Receiver:
    def __init__(self, host = '', port = 1881, local_control = False):
        self.unpacker = struct.Struct('f f f f ? ? ? ?')
        self.packer = struct.Struct('B')
        
        self.local = local_control
        self.SERVERHOST = host
        self.SERVERPORT = port
        self.sock = UDPServerInit(self.SERVERHOST, self.SERVERPORT)
        
        self.uart = serial.Serial("/dev/ttyAMA0",baudrate = 9600, timeout = 0.03)
        self.uart.open()
        
        
        self.joystick = None
        if local_control == True:
            self.joystick = joystickSetup()
                
        self.done = False
        
        print("Remote Server is active")
        print('Host Address: ', self.SERVERHOST)
        print('Port Number: ', self.SERVERPORT)
        
     
    def ClassExit(self):
        self.sock.close() 
        self.uart.close()
        pygame.quit()
        exit()
    
    def ClassClose(self):
        self.sock.close()
        self.uart.close()
        
    def determineVelocity(self, axisx, axisy):
        direction = 0
        magnitude = 0
        
        #scaling speed backward
        if axisy > 0.20 and axisx < 0.20 and axisx > -0.20:
            direction = 4
            magnitude = 1 if axisy > 0.70 else 0
        #scaling speed forward
        elif axisy < -0.20 and axisx < 0.20 and axisx > -0.20:
            direction = 1
            magnitude = 1 if axisy < -70 else 0
        #scaling rotational speed right    
        elif axisx > 0.20 and axisy < 0.20 and axisy > -0.20:
            direction = 2
            magnitude = 1 if axisx > 0.70 else 0 
        #scaling rotational speed left
        elif axisx < -0.20 and axisy < 0.20 and axisy > -0.20:
            direction = 3
            magnitude = 1 if axisy < -0.70 else 0
        else:
            direction = 0
            magnitude = 0
         
            
        velocity = (direction) | (magnitude << 3)
            
        return velocity
    
    def determineServo(self, axis_rx, axis_ry, center):
        servo_action = 0
        if center == True:
            servo_action = 7
        elif axis_rx < -0.3 and axis_ry < 0.3 and axis_ry > -0.30:
            servo_action = 2
        elif axis_rx > 0.3 and axis_ry < 0.3 and axis_ry > -0.30:
            servo_action = 1
        elif axis_ry > 0.3 and axis_rx < 0.30 and axis_rx > -0.30:
            servo_action = 4
        elif axis_ry < -0.3 and axis_rx < 0.30 and axis_rx > -0.30:
            servo_action = 3
        else:
            servo_action = 0
        
        return servo_action
            
            
    
    def testConnection(self):
        try:
            print('Waiting for connection...')
            data = self.sock.recvfrom(1024)
            message = data[0].decode('UTF-8')
            address = data[1][0] + ":" + str(data[1][1])
            print('Signal from: ' + address)
            print('Signal: ' + message)
            print('Signal Received, Connection Successful')
        except KeyboardInterrupt:
            self.ClassExit()
            
    def RunSingleIteration(self):
        axis_x = axis_y = axis_rx = axis_ry = 0.0
        tog_auto = tog_man = center = status = False
        
        
        for event in pygame.event.get(): # User did something
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.QUIT: #and event.key == pygame.K_ESCAPE:
                self.done = True
                
        if self.local == True:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            axis_rx = self.joystick.get_axis(2)
            axis_ry = self.joystick.get_axis(5)
            but_share = self.joystick.get_button(8)
            but_option = self.joystick.get_button(9)
            center = self.joystick.get_button(11)
            tog_auto = self.joystick.get_button(3)
            tog_man = self.joystick.get_button(1)
                        
            if but_share == True and but_option == True:
                status = True
            else:
                status = False
                
        else:
            packet, addr = self.sock.recvfrom(self.unpacker.size)
            axis_x, axis_y, axis_rx, axis_ry, center, status, tog_auto, tog_man = self.unpacker.unpack(packet)
            
        if status == True:
            self.done = True
        
        velocity = self.determineVelocity(axis_x, axis_y)
        servo_action = self.determineServo(axis_rx, axis_ry, center)
        state_switch = 0
        
        if tog_auto == True:
            uart_set = 0x81
            print("Setting Mode to Auto")
        elif tog_man == True:
            uart_set = 0x82
            print("Setting Mode to Manual")
        else:
            uart_set = (velocity) | (servo_action << 4)
                
        uart_signal = self.packer.pack(uart_set)
        

        
        #print("UART Signal: {0:b}".format(uart_signal))
        
        self.uart.write(uart_signal)
        
        '''
        serial_recv = self.uart.read(1)
        if(serial_recv != b''):
            state_rpm = self.packer.unpack(serial_recv)[0]
            state = "Automatic" if (state_rpm & 0xC0) == 0x80 else "Manual"
            rpm = state_rpm & 0x3F
            print("Mode: {}".format(state))
            print("RPM: {}".format(rpm))
            '''
        
            