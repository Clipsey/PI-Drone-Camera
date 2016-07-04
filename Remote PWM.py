import pygame
import socket
import struct
import time

def exitProgram(sock):
    sock.close()
    pygame.quit()
    exit()

def pygameSetup():
    pygame.init()
    pygame.display.set_mode((640,480))
    pygame.display.set_caption('UDP Client')
    pygame.mouse.set_visible(1)
    
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick
    
def clientSetup():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print("Failed to create socket")
        exitProgram(sock)
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

def UDPSend(sock, HOST, PORT, packet):
    try:
        sock.sendto(packet,(HOST, PORT))
    except socket.error as msg:
        print(msg)
        
def TestConnection(sock, HOST, PORT):
    try:
        print("Sending connection Signal...")
        signal = 'Remote Signal'
        UDPSend(sock, HOST, PORT, signal.encode('UTF-8'))
    except socket.error as msg:
        print(msg)
        exitProgram(sock)
    except KeyboardInterrupt:
        exitProgram(sock)
        
    input('Press Enter to Continue')
    


#SERVERHOST = input("Enter HOST: ")
#SERVERPORT = int(input("Enter PORT: "))
SERVERHOST = '192.168.0.205'
SERVERPORT = 1881
sock = clientSetup()
TestConnection(sock, SERVERHOST, SERVERPORT)
print("Connection Successful")

joystick = pygameSetup()

done = False
exit_button = False

connection_status = True
 
packer = struct.Struct('f f f f ? ?')
 
while done==False:
      
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN: #and event.key == pygame.K_ESCAPE:
            done = True
     
    axis_lx = joystick.get_axis(0)
    axis_ly = joystick.get_axis(1)
    axis_rx = joystick.get_axis(2)
    axis_ry = joystick.get_axis(3)
    but_share = joystick.get_button(8)
    but_option = joystick.get_button(9)
    but_cam_stick = joystick.get_button(11)

    if but_share == True and but_option == True and exit_button == False:
        exit_button = True
        print("Ending Connection")
         
    axis_pair = (axis_lx, axis_ly, axis_rx, axis_ry, but_cam_stick, exit_button)
    axis_pack = packer.pack(*axis_pair)
    
    UDPSend(sock, SERVERHOST, SERVERPORT, axis_pack)
    time.sleep(0.05)
        
exitProgram(sock)
