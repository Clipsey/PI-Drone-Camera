import socket
import pygame
import pygame.camera
import time

pygame.init()
pygame.camera.init()

class Drone_Webcam(object):
    def __init__(self, host = '', port = 9001):
        self.SERVERHOST = host
        self.SERVERPORT = port
        self.camlist = pygame.camera.list_cameras()
        self.webcam = pygame.camera.Camera(self.camlist[0],(640,360))
        self.webcam.start()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.close()
        
        self.done = False
        
    def ClassExit(self):
        self.sock.close()
        pygame.quit()
        exit()
    
    def ClassClose(self):
        self.sock.close()
        
    def ConnectServer(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print ('Socket Create failed')
            print(msg)
            self.ClassExit()
        
        try:
            self.sock.connect((self.SERVERHOST, self.SERVERPORT))
        except KeyboardInterrupt:
            self.ClassExit()
        
        
    def RunWebcam(self):
        try:
            while True:
                image = self.webcam.get_image()
                image_string = pygame.image.tostring(image, "RGB")
                self.ConnectServer()
                self.sock.sendall(image_string)
                self.sock.close()
                time.sleep(0.04)
                
        #=======================================================================
        # except socket.error as msg:
        #     print("Socket Error")
        #     pass
        #=======================================================================
        except KeyboardInterrupt:
            self.ClassExit()
            
    def RunSingleIteration(self):
        image = self.webcam.get_image()
        image_string = pygame.image.tostring(image,"RGB")
        self.ConnectServer()
        self.sock.sendall(image_string)
        self.sock.close()
                
        