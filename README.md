PiMPD_show

Python script for Raspberry Pi
Display pleing info on a small tft screem

Assumptions

1.You have a Raspberry Pi with a working mpd install. Tested with Raspberry Pi OS, moode audio player and Dietpi. It works well with moodeaudio especially for displaying radio station details.

2. You have a tft screen attached to the Raspberry Pi which has been set up as a framebuffer
3. You can ssh into the Raspberry Pi

Installation

1. Copy to your Raspberry Pi
   ```sh
   git clone https://github.com/rusconi/PiMPD_show.git
   ```
   ```sh
   cd PiMPD_show
   ```
2. make sure all python requirements are installed.
   ```sh
   sudo apt install python3-pil python3-mutagen python3-numpy python3-mpd python3-yaml -y
   ```
   At this point you can check that its working before you install the service.
   ```sh
   python mpdshow.py
   ```
   Some installations may require python3 instead of python

   If it works, stop the script and install
3. Full Installation
   This will install the script and its associated files in /opt/PiMPD_show, then install, enable and run it as a service.
   
