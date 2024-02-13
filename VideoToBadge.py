# How this works:
# 1. Put your video in the same folder as this script
# 2. Change the OrigVid variable to the name of your video file with its extension and optionally compressedFileName
# 3. Run the program. (Takes about 1 minute per 10-30 seconds of video)
# 4. Put the .gz file in to the animations folder along with the video script.
# 5. Update the video_file_name variable with the compressed file's name including it's extension.

import cv2
import math
import binascii
import gzip
import sys
import time
import numpy as np

###### Editables #####

OrigVid = "OriginalVideoName.avi"  # The original video file
compressedFileName = 'OutputFileName.gz'  # The file that the program exports to.
targetFPS = 5  # Frames per second the badge will play the video as. Lower = smaller file. Badge can only play back about 5 frames per second.
colorDepth = 24  # Can be 8 or 24. 8 = much smaller file size, but looks like hot garbage.
brightness = 1  # Can be used to dim the video. Between 0.0 and 1.0. Sometimes brighter videos can be annoying.
increaseContrast = False  # Can be enabled if things blend together too much.

######################

# Display is 7 x 18
dispH = 7
dispW = 18
dispFrame = ""
binFile = ""
frameCount = 0
startTime = time.time()

# Represents the positions of the missing pixels on the badge
# These are used to skip the spots in the display algorithm. Used to save ~14% on file size of the video
deadPixels0 = (0, 17) # The missing pixels on the first row
deadPixels5 = (7, 8, 9, 10) # The missing pixels on row 5
deadPixels6 = (0, 6, 7, 8, 9, 10, 11, 17) # The missing pixels on row 6

# Binary File to output the video file
outputFile = gzip.open(compressedFileName, 'wb')

# Make Video object
video = cv2.VideoCapture(OrigVid)

# Read first frame to determine size
test, frame = video.read()  # Pulls frame. "test" confirms it is available. "Frame" is the 3d RGB array data. height x width x R + G + B
video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Refers to first frame of the video
duration = video.get(cv2.CAP_PROP_FRAME_COUNT)
videoFPS = video.get(cv2.CAP_PROP_FPS)

# Initialize 3d array. Used to store a frame as would be seen on a badge
badgeFrame = np.zeros((dispH, dispW, 3)) # (y, x, RGB)

targetFrameDelay = 1000 / targetFPS
videoFrameDelay = 1000 / videoFPS
curFrameDelay = 0

# Determines the height/width of video. Cuts off any extra that doesn't fit neatly in to the display screen.
height = len(frame) - (len(frame) % dispH)
width = len(frame[0]) - (len(frame[0]) % dispW)

# Calculate how much to reduce the resolution of the video by
hReduct = int(math.floor(height / dispH))
wReduct = int(math.floor(width / dispW))

if video == False:
    print "ERROR: File not found"
    exit()

if videoFPS < targetFPS:
    print "ERROR: Target FPS can't be larger than the video's FPS"
    exit()

while video.grab(): # Gets the next frame. Returns false if it's at the end of the file.

    # Tracks the process progress and updates at each
    frameCount += 1
    percent = float(frameCount) / duration
    arrow = '=' * int(round(percent * 20) - 1) + 'D'
    spaces = ' ' * (20 - len(arrow))

    # Loading Bar
    sys.stdout.write("\rPercent: 8{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

    # Only saves a number of frames that match's the targetFPS
    curFrameDelay += videoFrameDelay
    if curFrameDelay >= targetFrameDelay:
        curFrameDelay -= targetFrameDelay
        test, frame = video.retrieve()

        for y in range(0, dispH, 1):  # A step for every vertical pixel on the badge
            for x in range(0, dispW, 1):  # Step for every horizontal pixel on the badge
                valR = 0
                valG = 0
                valB = 0
                # Add up the RGB values to be averaged out.
                for i in range(hReduct * y, (y+1) * hReduct, 1):  # Step for each pixel in the block in the original video frame
                    for j in range(wReduct * x, (x+1) * wReduct, 1):  # step for each pixel in the block of the original video frame
                        valR += frame[i][j][0]
                        valG += frame[i][j][1]
                        valB += frame[i][j][2]
                # Average the RGB values and add it to the badgeFrame numpy array.
                badgeFrame[y][x][0] = (float(valR) / (hReduct * wReduct))
                badgeFrame[y][x][1] = (float(valG) / (hReduct * wReduct))
                badgeFrame[y][x][2] = (float(valB) / (hReduct * wReduct))

        cv2.imwrite('badgeFrame.png', badgeFrame)
        badgeFrame = cv2.imread('badgeFrame.png')
        # Increase contrast
        if increaseContrast == True:
            # Convert from RGB to YUV due to the createCLAHE function outputs luminosity. YUV color supports luminosity shifts.
            badgeFrame_yuv = cv2.cvtColor(badgeFrame, cv2.COLOR_BGR2YUV)
            clahe = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(2, 3))  # Outputs a brightness/luminosity shift.
            badgeFrame_yuv[:, :, 0] = clahe.apply(badgeFrame_yuv[:, :, 0])  # Apply the brightness/luminosity shift to the frame
            badgeFrame = cv2.cvtColor(badgeFrame_yuv, cv2.COLOR_YUV2RGB)  # Convert back from yuv to RGB
            cv2.imwrite('badgeFrame2.png', badgeFrame)
        else: badgeFrame = cv2.cvtColor(badgeFrame, cv2.COLOR_BGR2RGB)


        for y in range(0, dispH, 1):  # A step for every vertical pixel on the badge
            for x in range(0, dispW, 1):  # Step for every horizontal pixel on the badge
                if not (y == 0 and x in deadPixels0):  # Skips the missing pixels on the badge
                    if not (y == 5 and x in deadPixels5):
                        if not (y == 6 and x in deadPixels6):
                            if colorDepth == 24:
                                # 24 bit RGB color is converted to binary ascii data. Two ascii characters for R, G, and B
                                RGBval = binascii.unhexlify(("00" + ("%x" % (badgeFrame[y][x][0] * brightness)))[-2:])
                                RGBval += (binascii.unhexlify(("00" + ("%x" % (badgeFrame[y][x][1] * brightness)))[-2:]))
                                RGBval += (binascii.unhexlify(("00" + ("%x" % (badgeFrame[y][x][2] * brightness)))[-2:]))
                                outputFile.write(RGBval)
                            elif colorDepth == 8:
                                # 8 bit color:
                                # It's a value between 0 and 255 represented as an ascii character. Red and green both get 3 bits while blue gets 2.
                                # red is 0 to 224. multiples of 32
                                # green is 0 to 28. multiples of 4
                                # blue is 0 to 3. multiples of 1
                                RGBval = round((float(badgeFrame[y][x][0]) / 36.43)) * 32
                                RGBval += round((float(badgeFrame[y][x][1]) / 36.43)) * 4
                                RGBval += round((float(badgeFrame[y][x][2]) / 85)) * 1
                                outputFile.write(binascii.unhexlify(("00" + ("%x" % RGBval))[-2:]))  # Converts to binary hex
                            else:
                                print "Error: colorDepth must be 8 or 24."
                                exit()

# Output how long the video processing took.
print "\nElapsed time: " + str(round(((time.time() - startTime) / 60), 1)) + " minutes."
outputFile.close()
