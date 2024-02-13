# Video-To-Defcon-Furs-Badge

VideoToBadge.py converts a video file to a compressed binary file. video.py uses the binary file to play that video on a 7 x 18 pixel RGB LED badge made by Defcon Furs.

It looks terrible, it doesn't have any sound, and you can barely tell that a video is being played. But I achieved my goal of playing full motion video of feature length on a small badge with 4MB of storage that was only intended to play simple pixel animations.

Using this script I was able to compress the entire bee movie (1 hour 31 minutes) and play it back on the badge at a blazing 5 frames per second and a vivid color bit depth of 8. /s

This script breaks up the video by frame and averages the sectors in to a single color for a pixel.
Each pixel in the frame is stored as either 8 or 24 bit depth. At 8 bit depth red and green get 7 options for intensity, but blue only gets 3 for a total of 255 different colors per pixel. This allows for very efficient storage usage. Each frame is just 896 bits (0.112kb) which is further compressed by gzip. This compressed data is uncompressed by the badge and streams the decompressed data directly to the display, which removes the need for extra storage in the memory. This allows for more video data to be crammed in to the memory and fill up the entire 4MB of space.

VideoToBadge.py converts and compresses the target video and video.py is ran on the badge to play back the video. View VideoToBadge.py for instructions to use it. 

The badge that this script was made for: https://github.com/defconfurs/dcfurs-badge-dc27
