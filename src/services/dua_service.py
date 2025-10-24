import asyncio
import pygame
import os


pygame.mixer.init()
current_channel = None

AUDIO_PATHS = {
    "morning": os.path.join("static", "audio", "morning_dua.mp3"),
    "evening": os.path.join("static", "audio", "evening_dua.mp3"),
}

async def play_dua_audio(dua_type: str):
    global current_channel
    if current_channel and current_channel.get_busy():
        current_channel.stop()
    if dua_type not in AUDIO_PATHS:
        return
    file_path = AUDIO_PATHS[dua_type]
    if os.path.exists(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        current_channel = pygame.mixer.find_channel()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.5)

async def stop_dua_audio():
    pygame.mixer.music.stop()
