"""Simple procedural SFX using pygame.mixer."""

import math
import wave
import io
import pygame


class Audio:
    def __init__(self):
        self.muted = False
        self.enabled = False
        self._sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._build_sounds()
        except pygame.error:
            self.enabled = False

    def _tone(self, freqs, duration=0.08, volume=0.35, decay=True):
        sample_rate = 22050
        n = int(sample_rate * duration)
        raw = bytearray()
        for i in range(n):
            t = i / sample_rate
            env = (1.0 - (i / n)) if decay else 1.0
            sample = 0.0
            for f, amp in freqs:
                sample += amp * math.sin(2 * math.pi * f * t)
            val = int(max(-1.0, min(1.0, sample * env * volume)) * 32767)
            raw += int(val).to_bytes(2, byteorder="little", signed=True)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bytes(raw))
        buf.seek(0)
        return pygame.mixer.Sound(file=buf)

    def _build_sounds(self):
        self._sounds["jump"] = self._tone([(520, 0.6), (780, 0.3)], 0.07, 0.3)
        self._sounds["double"] = self._tone([(660, 0.5), (990, 0.4)], 0.09, 0.28)
        self._sounds["land"] = self._tone([(180, 0.7)], 0.05, 0.25)
        self._sounds["collect"] = self._tone([(880, 0.4), (1320, 0.5)], 0.12, 0.3)
        self._sounds["hit"] = self._tone([(120, 0.8), (90, 0.5)], 0.18, 0.4)
        self._sounds["clear"] = self._tone([(523, 0.4), (659, 0.4), (784, 0.5)], 0.35, 0.32)
        self._sounds["select"] = self._tone([(440, 0.5)], 0.04, 0.2)
        self._sounds["ui"] = self._tone([(330, 0.4)], 0.03, 0.15)

    def play(self, name):
        if self.muted or not self.enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            snd.play()

    def set_muted(self, muted):
        self.muted = muted
