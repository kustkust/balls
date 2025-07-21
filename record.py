"""
PygameRecord - A utility for recording Pygame screens as GIFS.
This module provides a class, PygameRecord, which can be used to record Pygame
animations and save them as GIF files. It captures frames from the Pygame display
and saves them as images, then combines them into a GIF file.
Credits:
- Author: Ricardo Ribeiro Rodrigues
- Date: 21/03/2024
- source: https://gist.github.com/RicardoRibeiroRodrigues/9c40f36909112950860a410a565de667
Usage:
1. Initialize PygameRecord with a filename and desired frames per second (fps).
2. Enter a Pygame event loop.
3. Add frames to the recorder at desired intervals.
4. When done recording, exit the Pygame event loop.
5. The recorded GIF will be saved automatically.
"""

from datetime import datetime
from pathlib import Path
from threading import Thread

import numpy as np
import pygame
from PIL import Image


class PygameRecord:
    def __init__(self, filename: str, fps: int, n: int = 1):
        self.fps = fps
        self.filename = filename
        self.frames: list[Image.Image] = []
        self.n = n
        self.c = 0
        self.recording = False

    def switch(self) -> None:
        if not self.recording:
            self.recording = True
            self.c = 0
        else:
            self.recording = False
            Thread(target=self.save, daemon=True).start()

    def reset(self) -> None:
        self.frames = []

    def add_frame(self):
        self.c += 1
        if self.c < self.n or not self.recording:
            return
        self.c = 0
        curr_surface = pygame.display.get_surface()
        if curr_surface is None:
            return
        x3 = pygame.surfarray.array3d(curr_surface)
        x3 = np.moveaxis(x3, 0, 1)
        array = Image.fromarray(np.uint8(x3))
        self.frames.append(array)

    def save(self):
        if len(self.frames) == 0:
            return
        path = Path(self.filename.format(dt=datetime.now().strftime("%Y-%m-%d %H-%M-%S")))
        path.parent.mkdir(parents=True, exist_ok=True)
        self.frames[0].save(
            path,
            save_all=True,
            optimize=False,
            append_images=self.frames[1:],
            loop=0,
            format="gif",
            duration=int(1000 / (self.fps / self.n)),
        )
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred: {exc_value}")
        self.save()
        # Return False if you want exceptions to propagate, True to suppress them
        return False
