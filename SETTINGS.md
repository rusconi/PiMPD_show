The settings file 'settings.yaml', what each section is and how to edit it

1. Layout
    layout: 0

    There are 2 layout options:
    0 = standard
        For the 4:3 aspect ratio screen. e.g. 320px x 240px
    1 = horizontal
        For a wider, lower screen. e.g. 320px x 170px
        This has the cover image to the left half of the screen and the text next to the cover on the tight of the screen
        This will also display on 4:3 aspect ratio screans

    Edit the layout option to be 0 or 1

2. Default start screen for the standard layout
    defaultscreen: 0

    There are two options:
    0 = Background with text and status
    1 = Background with full cover, text and status

    Edit the layout option to be 0 or 1

3. Colours
    colors:
    Options to change the RGB codes for the colours of the 3 lines of text and the status line
        text1: [200, 255, 200]
        text2: [255, 240,99]
        text3: [200, 200, 255]
        status: [255, 255, 0]

    Find a colour picker online and enter the 3 RGB numbers for your colour of choice.
    The numbers are foron 0 to 255

4. Buttons
    Edit the gpio numbers to suit your buttons

    *** Buttons are optional and are NOT required for the script to operate ***

    buttons:
    
        text: 12
        pause: 4
        next: 6
        prev: 5

    These are the GPIO numbers [not the phisical pin numbers] that the button is connected to.
    The funcions of the buttons are;
    * text - cicles through 4 screen options for standard layout and 3 for horizontal
        the screens are:
        Standard
            Background with text and status
            Background with full cover, text and status
            Background with full cover
            Blanh Screen
        Horizontal
            Cover and text
            Cover only

    * pause - Toggles the playinf state between play and pause

    * next - jumps to the next track - does not work for radio streams

    * prev - jumps to the previous track - does not work for radio streams

5. Background image brightess
    artbrighness: 37

    The brightness of the image that is the screen background, usually the cover image
    Use a value between 0 and 100
    100 is tha same as the unprocessed cover image
    numbers higher than 100 will work as wll with varying degrees of success

6. Showstate
    showstate: True

    For the horizontal layout only
    If true a background icon of the state [play, pause or stop] will display behind the text.
    The other option is False

7. Logging
    log: False

    If True a log file will be appended with each screen update
    The format of the log is:
        date+time: title - artist - album(or radio station): state : script uptime

    This is mainly for tracking errors.  Be aware that the file could get large if left going for some time

    
T