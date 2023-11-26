import sys
import math
import wave
import numpy
import pygame
from pygame.locals import *
from scipy.fftpack import dct
import datetime
import os

N = 100  # num of bars
HEIGHT = 100  # height of a bar
WIDTH = 10  # width of a bar
FPS = 10

file_name = sys.argv[1]
status = 'stopped'

# Initialize Pygame and audio playback
pygame.init()
pygame.mixer.init()
fpsclock = pygame.time.Clock()  # Moved the declaration of fpsclock here
screen = pygame.display.set_mode([N * WIDTH, 50 + HEIGHT * 4])
pygame.display.set_caption('OASS - Open Audio Spectrum Software')
my_font = pygame.font.SysFont('consolas', 16)
pygame.mixer.music.load(file_name)
pygame.mixer.music.play()
pygame.mixer.music.set_endevent()
status = "playing"

# Process wave data
f = wave.open(file_name, 'rb')
params = f.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]
str_data = f.readframes(nframes)
f.close()
wave_data = numpy.fromstring(str_data, dtype=numpy.short)
wave_data.shape = -1, 2
wave_data = wave_data.T

num = nframes

# Rest of your code remains unchanged...


def visualizer(num):
    num = int(num)
    h = abs(dct(wave_data[0][nframes - num:nframes - num + N]))
    h = [int(i ** (1 / 2.5) * HEIGHT / 100) for i in h]
    draw_bars(h)

def vis(status):
    global num, params
    if status == "stopped":
        num = nframes
        return
    elif status == "paused":
        visualizer(num)
    else:
        num -= framerate / FPS
        if num > 0:
            visualizer(num)
    
    file_path = os.path.abspath(sys.argv[1])
    
    duration = nframes / framerate
    file_duration_info = f"Duration: {int(duration // 60)} min {int(duration % 60)} sec"
    file_duration_rendered = my_font.render(file_duration_info, True, (255, 255, 255))
    screen.blit(file_duration_rendered, (0, 54))

    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)  # Convert to megabytes
    file_size_info = f"File Size: {file_size_mb:.1f} MB"
    file_size_rendered = my_font.render(file_size_info, True, (255, 255, 255))
    screen.blit(file_size_rendered, (0, 72))

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_info = f"Current Date: {current_date}"
    date_rendered = my_font.render(date_info, True, (255, 255, 255))
    text_width, _ = my_font.size(date_info)
    screen.blit(date_rendered, (screen.get_width() - text_width, 0))

    # Other audio file information
    # ...

def get_time(): 
    seconds = max(0, pygame.mixer.music.get_pos() / 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms = ('%02d:%02d:%02d' % (h, m, s))
    return hms

def controller(key):
    global status
    if status == 'stopped':
        if key == K_RETURN:
            pygame.mixer.music.play()
            status = 'playing'
    elif status == 'paused':
        if key == K_RETURN:
            pygame.mixer.music.stop()
            status = 'stopped'
        elif key == K_SPACE:
            pygame.mixer.music.unpause()
            status = 'playing'
    elif status == 'playing':
        if key == K_RETURN:
            pygame.mixer.music.stop()
            status = 'stopped'
        elif key == K_SPACE:
            pygame.mixer.music.pause()
            status = 'paused'

def draw_bars(h):
    for i, height in enumerate(h):
        # Interpolating color based on bar height
        hue = 240 - (height / HEIGHT) * 65  # Hue variation from blue to red
        if hue < 0:
            hue = 0
        color = pygame.Color(0, 0, 0)
        color.hsla = (hue % 360, 100, 50, 100)  # Set hue for colorful gradient

        # Draw bar with color gradient
        pygame.draw.rect(screen, color, (i * WIDTH, 50 * 7 + HEIGHT - height, WIDTH - 1, height))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            controller(event.key)

    if num <= 0:
        status = 'stopped'

    name = my_font.render(sys.argv[1], True, (255, 255, 255))
    info = my_font.render(status.upper() + ' ' + get_time(), True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(name, (0, 0))
    screen.blit(info, (0, 18))
    fpsclock.tick(FPS)
    vis(status)

    pygame.display.update()
