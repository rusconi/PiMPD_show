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
   The shell script pimpd_manager.sh allows you to install or uninstall the scripts and service as well as starting, stopping, restarting or getting the status of the service
   Usage: pimpd_manager.sh {install|uninstall|start|stop|restart|status}

   to install the script must be run as superuser
   ```sh
   sudo bash pimpd_manager.sh install
   ```

Usage

There are options for 4 buttons
text
pause
next
prev
The settings file 'settings.yaml' describes their actions
To edit
```sh
bash edit_settings.sh
```
The darkness of the background image can be adjusted in settings.yaml
the layout options between standard [e.g. 320x240] oe horizontal [e.g. 170x320] can be changed in settings.yaml
Each time you change the settings run
```sh
sudo bash pimpd_manager.sh restart
```
so they take effect


   

   
