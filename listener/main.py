import uuid
from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError
import threading
import queue


class Listener:
    def __init__(self, logger):
        self.log = logger
        self.recognizer = Recognizer()

        self.listening = False
        self.paused = False

        self.speech_queue = queue.Queue()
        self.listener_thread = threading.Thread(target=self.run_listener, daemon=True)
        self.log.debug("Listener initialized.")

    def start_listening(self):
        self.listening = True
        if not self.listener_thread.is_alive():
            self.listener_thread.start()
            self.log.debug("Starting listener...")

    def stop_listening(self):
        self.listening = False
        if self.listener_thread.is_alive():
            self.listener_thread.join()
            self.log.debug("Stopping listener...")

    def pause_listening(self):
        self.paused = True

    def resume_listening(self):
        self.paused = False

    def run_listener(self):
        while self.listening:
            if self.paused:
                continue

            with Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source=source, duration=1)
                audio = self.recognizer.listen(source)

                try:
                    text = self.recognizer.recognize_google(audio)
                    self.speech_queue.put(text)
                    self.log.info(f"Recognized speech: {text}")

                except UnknownValueError:
                    self.log.debug(
                        "Picked up noise, but didn't recognize it as human voice. Ignoring."
                    )

                except RequestError:
                    self.log.error(
                        "Could not request results from Google Speech Recognition service"
                    )

    def get_speech_event(self):
        try:
            event = self.speech_queue.get_nowait()
            return event, uuid.uuid4()
        except queue.Empty:
            return None, None
