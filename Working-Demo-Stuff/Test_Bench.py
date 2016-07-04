import pygame
import Drone_Controller_Module
import Drone_Webcam_Module
import time
import threading
import socket

drone_quit = False

def ControllerThreadLoop(Controller):
    global drone_quit
    while Controller.done == False and drone_quit == False:
        try:
            Controller.RunSingleIteration()
            time.sleep(0.05)
        except KeyboardInterrupt:
            drone_quit = True
            exit()
            
    drone_quit = True
    exit()
    
def CameraThreadLoop(Camera):
    global drone_quit
    while Camera.done == False and drone_quit == False:
        try:
            Camera.RunSingleIteration()
            time.sleep(0.04)
        except (KeyboardInterrupt, socket.error):
            drone_quit = True
            exit()
            
    drone_quit = True        
    exit()
    
pygame.init()

Controller = Drone_Controller_Module.Drone_Receiver('',1881, False)
#ControllerThreadLoop(Controller)

Drone_Cam = Drone_Webcam_Module.Drone_Webcam('192.168.137.1',9001)

Control_thread = threading.Thread(target=ControllerThreadLoop,args=(Controller,))
Camera_thread = threading.Thread(target=CameraThreadLoop,args=(Drone_Cam,))

Control_thread.start()
input("Press Enter to start Webcam Thread")
Camera_thread.start()

Control_thread.join()
Camera_thread.join()

Controller.ClassClose()
Drone_Cam.ClassClose()

pygame.quit()
exit()