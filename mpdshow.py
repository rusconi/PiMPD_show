#!/usr/bin/python3
#


from mpd import MPDClient
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter #, ImageStat, ImageColor, ImageOps
from framebuffer import Framebuffer  # pytorinox
import time
import os
import os.path
from os import path
import sys
from mutagen import File
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
import io
from io import BytesIO
import yaml
from pprint import pprint
import textwrap
import requests
import RPi.GPIO as GPIO
import re
import configparser
import logging


script_path = os.path.dirname(os.path.abspath( __file__ ))
START_TIME = time.time()
confile = 'settings.yaml'
# set script path as current directory - 
os.chdir(script_path)

if os.path.exists('/dev/fb1'):
    fb = Framebuffer(1)
    #print("/dev/fb1 exists")
    # You can then proceed with code that uses the framebuffer
else:
    fb = Framebuffer(0)
    #print("/dev/fb1 does not exist")
    # Handle the case where the device is not available

scr_width = fb.size[0]
scr_height = fb.size[1]

# Configure the logger to save to 'app.log'
logging.basicConfig(
    filename='pimpd.log', 
    filemode='a', # 'a' for append (default), 'w' for overwrite
    format='%(asctime)s: %(message)s', #'%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_uptime():
    """Returns the uptime of the script in a readable format."""
    uptime_seconds = time.time() - START_TIME
    return time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

def load_config(confile):
    try:
        with open(confile, 'r') as file:
            config_data = yaml.safe_load(file)
            colors = config_data.get('colors')
            buttons = config_data.get('buttons') 
            layout = config_data.get('layout')
            brightness = config_data.get('artbrighness')
            showstate = config_data.get('showstate')
            log = config_data['log']
            
    except FileNotFoundError:
        # set defaults in case config file doesn't exist
        colors = {'text1': [255, 255, 255], 'text2': [255, 255, 255], 'text3': [255, 255, 255], 'status': [255, 255, 255]}
        buttons = {'text': 6, 'pause': 12, 'next': 4, 'prev': 5}
        layout = 0
        brightness = 50
        showstate = False
        log = False

    return colors, buttons, layout, brightness, showstate, log

colors, buttons, layout, brightness, showstate, log = load_config(confile)

cover_brightness = brightness / 100

txt_b = buttons['text']
plp_b = buttons['pause']
nxt_b = buttons['next']
prv_b = buttons['prev']

text1_col = colors.get('text1')
text1_color = (text1_col[0], text1_col[1], text1_col[2], 255)
text2_col = colors.get('text2')
text2_color = (text2_col[0], text2_col[1], text2_col[2], 255)
text3_col = colors.get('text3')
text3_color = (text3_col[0], text3_col[1], text3_col[2], 255)
status_col = colors.get('status')
status_color = (status_col[0], status_col[1], status_col[2])

cover_only = 0

song_text = configparser.ConfigParser()

status_backgrounds = {
    "play": Image.open(script_path + '/images/play_large.png'),
    "pause": Image.open(script_path + '/images/pause_large.png'),
    "stop": Image.open(script_path + '/images/stop_large.png')
}


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
BUTTON_PINS = [6, 5, 4, 12]
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    

def button_callback(channel):
    """
    This function is called by any button press event.
    The 'channel' argument identifies the specific pin that was triggered.
    """
    global layout
    client = MPDClient()
    client.timeout = None  # Important: idle can take a long time
    client.connect("localhost", 6600)
    song = client.currentsong()
    status = client.status()
    if channel == txt_b:
        max_cycles = 3 - layout
        
        #print("Button 1 (Pin 17) was pressed!")
        # Add specific actions for Button 1 here
        # Change the boolean value when button presses
        global cover_only
        cover_only = cover_only + 1
        if cover_only > max_cycles: cover_only = 0
        #update display
        mpd_display(client)
    else:
        
        source = 'library'
        if 'file' in song:
            if (song['file'].find('http://', 0) > -1) or (song['file'].find('https://', 0) > -1):
                # set radio stream to true
                source = 'radio'
            current_state = status.get('state')
            if channel == plp_b:
                #print("Button 2 (Pin 27) was pressed!")
                # Add specific actions for Button 2 here           
                if current_state == 'play':
                # Pause playback
                    client.pause(1)
                    #print("Playback paused.")
                elif current_state == 'pause' or current_state == 'stop':
                    client.play()
                    #print("MPD is already paused.")
                    # Toggling pause/resume can also be done by calling client.pause(1) or client.pause(0)
            if source == 'library':
                if channel == prv_b:
                    x = 'prev'
                    #print('prev')
                    client.previous()
                elif channel == nxt_b:
                    x = 'next'
                    #print('next')
                    client.next()
    


for pin in BUTTON_PINS:
    GPIO.add_event_detect(
        pin, 
        GPIO.FALLING, # Use FALLING if using PUD_UP, RISING if using PUD_DOWN
        callback=button_callback, 
        bouncetime=500 # Debounce time to prevent multiple triggers
    )


buffer = Image.new(mode="RGBA", size = fb.size)
black_scr = Image.new(mode="RGBA", size = fb.size)

def get_mpd_music_dir(config_path="/etc/mpd.conf"):
    # Common locations if default isn't found: 
    # ~/.config/mpd/mpd.conf or ~/.mpdconf
    config_path = os.path.expanduser(config_path)
    
    if not os.path.exists(config_path):
        return f"Config file not found at {config_path}"

    with open(config_path, 'r') as f:
        for line in f:
            # Match lines starting with music_directory (ignoring whitespace/comments)
            match = re.match(r'^\s*music_directory\s+"?([^"]+)"?', line)
            if match:
                return os.path.expanduser(match.group(1))
    
    return None

def get_apple_cover(artist, song):
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": f"{artist} {song}",
        "media": "music",
        "entity": "song",
        "limit": 1
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['resultCount'] > 0:
        # Get the largest artwork (artworkUrl100 -> 1000x1000)
        artwork_url = data['results'][0]['artworkUrl100'].replace('100x100bb.jpg', '1000x1000bb.jpg')
        #return artwork_url
        response = requests.get(artwork_url)
            
        image_data = BytesIO(response.content)
                
        # Open the image using Pillow and return the Image object
        image = Image.open(image_data).resize((480,480), Image.LANCZOS)

        return image
        

    else:
        return None


def radio_text(mpd_client):
    x=0
    mpd_song = mpd_client.currentsong()
    mpd_status = mpd_client.status()
    radio_name = ""
    radio_artist = ""
    radio_title = ""

    song_dict = {}
    try:
        with open('/var/local/www/currentsong.txt', 'r') as f:
            for line in f:
                if '=' in line:
                    moode = True
                    # Splits at the first '=' and removes surrounding whitespace
                    key, value = line.strip().split('=', 1)
                    song_dict[key.strip()] = value.strip()
                    #print('currentsong')
                    #pprint(song_dict)
                    #print('++++++++++++++++++++++++')
    except FileNotFoundError:
        moode = False
     
    if "name" in mpd_song: 
        radio_name = mpd_song.get('name')
    elif moode is True:
        radio_name = song_dict.get('album')
    elif "lastloadedplaylist" in mpd_status:
        llpl = mpd_status.get('lastloadedplaylist')
        radio_name = llpl.replace('RADIO/', '').replace('.pls', '')
        #radio_name = 'Last Resort'

    if "title" in mpd_song:
        radio_artist = mpd_song.get('title')

        if mpd_song['title'].find(' - ', 0) > -1:
            (radio_artist, radio_title) = mpd_song['title'].split(' - ', 1)

    return {'top':radio_title, 'middle':radio_artist, 'bottom':radio_name}

def get_file_cover(file_path):
    root, extension = os.path.splitext(file_path)
    file_type = extension[1:]
    img = Image.new(mode="RGBA", size=(320, 320))
    #print(file_type)
    if file_type == 'flac':
        # Extract cover art
        #ack_img = get_flac_cover(file_path)
        x=1
        audio = FLAC(file_path)
        for picture in audio.pictures:
            if picture.type == 3: # 3 is "Cover front"
                image_data = picture.data
                img = Image.open(io.BytesIO(image_data)).resize((480,480), Image.LANCZOS)
                
            else:
                img = start_img

    elif file_type == 'mp3':
        try:
            # Load the MP3 file with ID3 tags
            audio = MP3(file_path, ID3=ID3)
            
            # Look for the 'APIC' (Attached Picture) tag
            cover_art = None
            for tag in audio.tags.getall("APIC"):
                # Type 3 is the code for the front cover image
                if tag.type == 3: 
                    cover_art = tag
                    break
            
            if cover_art:
                # Get the image data as bytes
                image_data = cover_art.data
                
                # Use Pillow to open the image from bytes
                img = Image.open(BytesIO(image_data)).resize((320,320), Image.LANCZOS)
            else:
                #print(f"No front cover art found in {file_path}.")
                img = start_img
                
        except Exception as e:
            #print(f"An error occurred: {e}")
            x=1

    else:
        img = start_img
    
    return img




def mpd_display(mpd_client):
    x=8
    global start_img
    mpd_song = mpd_client.currentsong()
    '''print('song:')
    pprint(mpd_song)
    print('-------------------------------------')
    print('status')'''
    mpd_status = mpd_client.status()
    '''pprint(mpd_status)
    print('--------------------------------------')'''
    if 'file' in mpd_song:
            file_uri = mpd_song['file']
            first_four = file_uri[:4]
            if first_four == 'http':
                source = 'RADIO'  
                radio_txt = radio_text(mpd_client)
                top = radio_txt.get('top')
                middle = radio_txt.get('middle')
                bottom = radio_txt.get('bottom')         
                cover_img = get_apple_cover(middle, top)
                if cover_img is None:
                    cover_img = Image.open(script_path + '/images/background_radio.jpg')
                    
                if layout == 0:
                    screen_fill_std(radio_txt, cover_img, mpd_status, source)  
                else:
                    screen_fill_horiz(radio_txt, cover_img, mpd_status, source)

                
            else:
                source = 'LIBRARY'   
                music_dir = get_mpd_music_dir()
                if music_dir is not None:
                    file_path = os.path.join(music_dir, mpd_song['file'])
                    cover_img = get_file_cover(file_path)
                else:
                    cover_img = Image.open(script_path + '/images/mpd_480.png')

                file_text = {'top':mpd_song.get('title', '-'), 'middle':mpd_song.get('artist', '-'), 'bottom':mpd_song.get('album', '-')}
                if layout == 0:
                    screen_fill_std(file_text, cover_img, mpd_status, source)    
                else:
                    screen_fill_horiz(file_text, cover_img, mpd_status, source) 


        
    x=0

        #buffer.paste(image, (0, 0))
        #fb.show(buffer)

    
#******  Standard didplay ******************
#
def screen_fill_std(screen_text, cover_image, mpd_status, source):

    back_img = Image.new(mode="RGBA", size=fb.size)
    scr_width, scr_height = fb.size
    txt_ht = int((scr_height*8)/10)
    font_size = int(txt_ht/8)
    p_off = int(font_size * 1.5)
    y_offset = int((scr_height - scr_width) / 2)
    enhancer = ImageEnhance.Brightness(cover_image)
    # Darken the image by 50% (factor 0.5)
    # You can adjust the factor as needed (e.g., 0.8 for a lighter darken)
    #print(f"Cover Brightness: {cover_brightness}")
    dark_cover_img = enhancer.enhance(cover_brightness)
    dark_cover_img = dark_cover_img.resize((scr_width,scr_width), Image.LANCZOS)
    back_img.paste(dark_cover_img, (0, y_offset))
    front_img = cover_image.resize((scr_height,scr_height), Image.LANCZOS)

    if cover_only == 1 or cover_only == 2:
        back_img.paste(front_img, (int((scr_width-scr_height)/2), 0))

    if cover_only < 2:
        #back_img.paste(black_scr)
        #fb.show(buffer)
   
        back_img = add_text(screen_text['top'], back_img, p_off, text1_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 28, 0)

        back_img = add_text(screen_text['middle'], back_img, int(txt_ht/2), text2_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 28, 0)

        back_img = add_text(screen_text['bottom'], back_img, txt_ht - p_off, text3_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 28, 0)

        status_bar(back_img, mpd_status, source, font_size)

    #back_img = back_img.resize((scr_width,scr_width), Image.LANCZOS)
    if log is True:
        logdata = mpd_status.get('title','#')+ " - " +  mpd_status.get('artist','#') + ' - ' + mpd_status.get('album','#') + ' : ' + mpd_status['state'] + ' : ' + get_uptime()
        logging.info(logdata)

    

    if cover_only == 3:
        fb.clear()
    else:
        buffer.paste(back_img, (0, 0))
        fb.show(buffer)


def status_bar(back_img, mpd_status, source, font_size):

    symfont = ImageFont.truetype(script_path + '/fonts/Font Awesome 7 Free-Regular-400.otf',font_size)
    symfont2 = ImageFont.truetype(script_path + '/fonts/Font Awesome 7 Free-Solid-900.otf',font_size)
    bottom_offset = int(font_size * 1.5)
       
    current_state = mpd_status['state']
    draw = ImageDraw.Draw(back_img)
    i_width, i_height = back_img.size


    #draw.rounded_rectangle((20, 360, 460, 396), radius=6, fill=(100,100,100,50), outline=(255, 200, 55,125), width=1)
    match current_state:
        case 'play':
            draw.text((40, i_height - font_size + 5), '\uf144', fill=status_color, font=symfont, anchor="mm" )
        case 'pause':
            draw.text((40, i_height - font_size + 5), '\uF28C', fill=status_color, font=symfont, anchor="mm" )
        case 'stop':
            draw.text((40, i_height - font_size + 5), '\uF28E', fill=status_color, font=symfont, anchor="mm" )

    if source == 'LIBRARY':
       
        draw.text((i_width/2, i_height - font_size + 5), '\uF1C7', fill=status_color, font=symfont, anchor="mm" )
       
    elif source == 'RADIO':
        
        draw.text((i_width/2, i_height - font_size + 5), '\uF8D7', fill=status_color, font=symfont2, anchor="mm" )
        

    s = i_width - 85
    t = i_height - 12
    vol = round(int(mpd_status['volume'])/9)
    #print(vol)
    if vol == 0:
        draw.text((i_width - 40, i_height - font_size +5 ), '\uf6a9', fill=status_color, font=symfont2, anchor="mm" )
    else:    
        vfill = (100,100,100,50)
        for i in range(10):
            x = (i*8)+s
            vfill = None
            if (i < (vol-1)):
                vfill = status_color
            draw.rectangle((x,t,x+5, i_height - 6), fill=vfill, outline=status_color, width=1)
            t = t-2

    return back_img
#
#------------------------------------------
#****  Horizontal Display  ****************
#
def screen_fill_horiz(screen_text, cover_image, mpd_status, source):
    #height = 226

    back_img = Image.new(mode="RGBA", size=fb.size)
    scr_width, scr_height = fb.size
    i_width, i_height = back_img.size

    state_img = status_backgrounds.get(mpd_status['state'])
    
    panel_dimension = int(scr_width/2)
    ypos = int((scr_height - panel_dimension)/2)
    state_img = state_img.resize((panel_dimension,panel_dimension), Image.LANCZOS)
    txt_back_img = Image.new(mode="RGBA", size=(panel_dimension, panel_dimension))
    big_cover = cover_image.resize((scr_height, scr_height), Image.LANCZOS)
    cover_image = cover_image.resize((panel_dimension, panel_dimension), Image.LANCZOS)

    if showstate is True: txt_back_img.paste(state_img)
    
    enhancer = ImageEnhance.Brightness(txt_back_img)
    # Darken the image by 50% (factor 0.5)
    # You can adjust the factor as needed (e.g., 0.8 for a lighter darken)
    #print(f"Cover Brightness: {cover_brightness}")
    txt_back_img = enhancer.enhance(0.18)
    txt_back_img = txt_back_img.convert('RGB')
    font_size = int(panel_dimension/10)
    p_off = int(font_size * 1.5)
    #back_img.paste(back_cover_img, (0, -40))

    
    if cover_only == 1:
        back_img.paste(big_cover, (int((scr_width-scr_height)/2), 0))
    elif cover_only == 0:
        back_img.paste(cover_image, (0, ypos))
        txt_back_img = add_text(screen_text['top'], txt_back_img, p_off, text1_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 18, 80)

        txt_back_img = add_text(screen_text['middle'], txt_back_img, panel_dimension/2, text2_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 18, 80)

        txt_back_img = add_text(screen_text['bottom'], txt_back_img, panel_dimension-p_off, text3_color, script_path + '/fonts/Roboto-Medium.ttf', font_size, 18, 80)

        back_img.paste(txt_back_img, (panel_dimension, ypos))


    '''if fb.size == (480,320):
        print('spot on')
    else:
        print('Resize it')
        back_img = back_img.resize((fb.size), Image.LANCZOS)'''
    
    if log is True:
        logdata = mpd_status.get('title','#')+ " - " +  mpd_status.get('artist','#') + ' - ' + mpd_status.get('album','#') + ' : ' + mpd_status['state'] + ' : ' + get_uptime()
        logging.info(logdata)

    if cover_only > 1:
        fb.clear()
    else:
        buffer.paste(back_img, (0, 0))
        fb.show(buffer)



#
#------------------------------------------

def add_text(text, img, y_pos, colour, font_path, font_size, txt_width, x_offset):

    #print(f'Font Size = {font_size}')
    i_width, i_height = img.size
    lesser_font_size = font_size - 2
    x=6
    txtfont = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img)
    if len(text) > txt_width:
        text = '\n'.join(textwrap.wrap(text, width=txt_width))
        txtfont = ImageFont.truetype(font_path, lesser_font_size)
    bbox = draw.multiline_textbbox((0, 0), text, font=txtfont)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    #print(f'text size:\nw = {text_width}\nh = {text_height}')
    
    x = ((i_width - text_width) / 2)
    y = y_pos - (text_height/2)
    draw.fontmode = "L"
    draw.multiline_text((x, y), text, font=txtfont, fill=colour, align="center")
                        
    return img



def monitor_mpd():
    client = MPDClient()
    client.timeout = None  # Important: idle can take a long time
    client.connect("localhost", 6600)
    current_song = client.currentsong()
    status = client.status()
    '''pprint(current_song)
    print('**************************')
    pprint(status)
    print(f"x")'''
    mpd_display(client)
    
    while True:
        # idle('player') blocks until the song changes, 
        # player stops, or seeks.
        client.idle('player', 'mixer')
        width = 50
        pad_char = " "
        current_song = client.currentsong()
        #pprint(current_song)
        status = client.status()
        #pprint(status)
        mpd_display(client)
        
        
def main():
    try:
        monitor_mpd()
        x=0
    except KeyboardInterrupt:
        fb.clear()
        print("\nStopped.") 
        

# Run the monitoring function
if __name__ == "__main__":
    main()