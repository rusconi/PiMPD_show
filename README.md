PiMPD_show

A python script to display mpd (music player daemon) now playing details on a small tft screen attached to a Raspberry Pi.

It was written for screens with a 4:3 aspect ratio. e.g. 320x240, 480x320 etc and should scale to suit, but has not been tested, so no guarantees., There is also has an option with a different screen layout that suits the1.9 inch 170x320 st7789 display.



It should work with most Raspberry Pis but has not been tested pn a Pi1 or Pi2.

Assumptions

You have a Raspberry Pi with a working mpd install. Tested with Raspberry Pi OS, moode audio player and Dietpi.

It works well with moodeaudio especially for displaying radio station details.



The script displays on a framebuffer set up for your display of choice.

This README will go through the steps for spi tft displays.



Ensure you have a frambeffer for your display.

The displays tested are 2.8 inch ili9341 tft, a 2.0 inch st7789 tft, a 1.9 inch st7789 tft, a 1.8 inch st7735 tft and 3.5 inch ili9486 tft.

The smaller the display, the smaller the text. The 1.8 inch st7735 only has a 160x128 pixel resolution, so the text is extremely small



Here are some examples to get the framebuffer working.

The pins used for reset, dc and backlight(led) were chosen to avoid pin conflicts with DAC hats.
If you use these overlays, connect the TFT as follows, otherwise edit the overlay line to suit your pin selection

| Display   | RPi pin | GPIO # |
| --------- | ------- | ------ |
| VCC       | 1       | 3.3v   |
| GND       | 6       | gnd    |
| CS        | 24      | 8      |
| RESET     | 11      | 17     |
| DC        | 13      | 27     |
| SDI(MOSI) | 19      | 10     |
| SCK       | 23      | 11     |
| LED       | 33      | 13     |

SSH into the raspberry pi

edit the /boot/firmware/config.txt file;

```bash
sudo nano /boot/firmware/config.txt
```

at the end if the file add the following to turn spi on

```bash
dtparam=spi=on
```

after this add the overlay details for your display

For ili9341

```bash
dtoverlay=fbtft,spi0-0,ili9341,reset_pin=17,dc_pin=27,cs=0,led_pin=13,rotate=270,bgr=1
```

for st7789 [same for 2.0 inch 320x240 and 1.9 inch 170x320]

```bash
dtoverlay=fbtft,spi0-0,st7789v,reset_pin=17,dc_pin=27,cs=0,led_pin=13,rotate=270
```

for st7735

```bash
dtoverlay=fbtft,spi0-0,adafruit18,speed=32000000,reset_pin=17,dc_pin=27,led_pin=13,rotate=270
```

save the edited file [Ctrl-c, y, enter]

now reboot the raspberry pi

After reboo ssh back into the pi

Check to see if a framebuffer has been set up for your display.

```bash
ls /dev/fb*
```

the result should be

```bash
/devfb0
```

or

```bash
/dev/fb0  /dev/fb1
```

depending on your hdmi setup.

The script will use fb1 if available, or fb0 if not

Get details of the framebuffer: [if fb1 dies not exist ise fb0 instead]

```bash
fbset -fb /dev/fb1 --info
```

the result should be like this

```bash
mode "320x240"
    geometry 320 240 320 240 16
    timings 0 0 0 0 0 0 0
    nonstd 1
    rgba 5/11,6/5,5/0,0/0
endmode

Frame buffer device information:
    Name        : fb_st7789v
    Address     : 0
    Size        : 153600
    Type        : PACKED PIXELS
    Visual      : TRUECOLOR
    XPanStep    : 0
    YPanStep    : 0
    YWrapStep   : 0
    LineLength  : 640
    Accelerator : No

```
