#!/usr/bin/python3
from framebuffer import Framebuffer
import os.path

if os.path.exists('/dev/fb1'):
    fb = Framebuffer(1)
    #print("/dev/fb1 exists")
    # You can then proceed with code that uses the framebuffer
else:
    fb = Framebuffer(0)
    #print("/dev/fb1 does not exist")
    # Handle the case where the device is not available

fb.clear()
