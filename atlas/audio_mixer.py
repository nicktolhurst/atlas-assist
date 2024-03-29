import os
import threading
import time
import pygame

class Mixer:
    def __init__(self, logger):
        self.log = logger
        self.queue = []
        self.stop_event = threading.Event()

    def init_mixer(self, log):
        try:
            pygame.init()
            pygame.mixer.init()
            log.success("Mixer initialized.")
        except pygame.error as e:
            log.error(f"Mixer initialization failed: {e}")

    def add_clip(self, clip):
        self.queue.append(clip)
        self.log.debug(f"Added clip: `{clip}`.")

    def start_auto_play_loop(self):
        while not self.stop_event.is_set():
            if self.queue:
                clip = self.queue.pop(0)
                self.play(clip)
            else:
                self.log.trace("Queue is empty, waiting...")
                self.stop_event.wait(1)
        self.log.debug("Thread stopped.")

    def stop_auto_play_loop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.stop_event.set()
        self.log.debug("Stop event detected.")

    def play(self, clip):
        pygame.mixer.music.load(clip)
        pygame.mixer.music.play()
        self.log.debug(f"Playing clip: {clip}")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        threading.Thread(target=self.delete_clip_from_disk, args=(clip,)).start()

    def is_playing(self):
        return pygame.mixer.music.get_busy() or self.queue

    def wait_for_finish(self):
        while self.is_playing():
            self.log.trace(f"Waiting for playback to finish...")
            time.sleep(1)

    def delete_clip_from_disk(self, clip):
        try:
            os.remove(clip)
            self.log.debug(f"Deleted file: {clip}")
        except Exception as e:
            self.log.error(f"Error deleting file {clip}: {e}")
