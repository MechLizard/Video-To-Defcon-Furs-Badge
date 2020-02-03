import uzlib
import dcfurs

# Video File you want to play
video_file_name = "beemovie_2.7fps_24color_1bright_nocontrast.gz"

# Frame Rate that was used to process the video file
frameRate = 7

# Can be 8 or 24. Enter what was used to process the video
colorDepth = 24

videoFile = open("animations\\" + video_file_name, 'rb')
decoder = uzlib.DecompIO(videoFile, 31)

class video:
    global frameRate

    def __init__(self):
        global frameRate
        self.interval = int(1000 / frameRate)

    def draw(self):
        global frameRate
        global decoder
        global videoFile
        global colorDepth

        if colorDepth == 8: frameSize = 112
        elif colorDepth == 24: frameSize = 336

        # Represents the positions of the missing pixels on the badge
        # These are used to skip the spots in the display algorithm. Used to save ~14% on file size of the video
        deadPixels0 = (0, 17) # The missing pixels on the first row
        deadPixels5 = (7, 8, 9, 10) # The missing pixels on row 5
        deadPixels6 = (0, 6, 7, 8, 9, 10, 11, 17) # The missing pixels on row 6

        framePos = 0

        frame = decoder.read(frameSize)  # The amount of bytes per frame

        # Reloads the video file if it reaches the end.
        if frame == b'':
            del decoder
            videoFile.close()
            videoFile = open("animations\\" + video_file_name, 'rb')
            decoder = uzlib.DecompIO(videoFile, 31)
            frame = decoder.read(frameSize)

        for y in range(0, 7, 1):  # A step for every vertical pixel on the badge
            for x in range(0, 18, 1):  # Step for every horizontal pixel on the badge
                if not (y == 0 and x in deadPixels0): # Skips missing pixels
                    if not (y == 5 and x in deadPixels5):
                        if not (y == 6 and x in deadPixels6):
                            #testnum = ord(frame[framePos])
                            if colorDepth == 24:
                                dcfurs.set_pix_rgb(x, y, int.from_bytes(frame[framePos * 3: framePos * 3 + 3], "big"))
                            elif colorDepth == 8:
                                dcfurs.set_pixel(x, y, frame[framePos])
                            framePos += 1
