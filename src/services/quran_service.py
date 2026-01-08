# quran_service.py

import httpx
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = None
TAFSIR_CACHE = {}
AUDIO_CACHE = {}
TIMESTAMP_CACHE = {}
BASE_URL = "https://api.quran.com/api/v4"
MISHARY_RECITER_ID = 7


async def get_timestamps(reciter_id: int, surah_number: int):
    key = f"{reciter_id}:{surah_number}"
    if key in TIMESTAMP_CACHE:
        cached, expiry = TIMESTAMP_CACHE[key]
        if datetime.utcnow() < expiry:
            return cached
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/chapter_recitations/{reciter_id}/{surah_number}",
            params={"segments": True},
        )
        if res.status_code != 200:
            logging.error(f"API Error: Failed to fetch timestamps for Surah {surah_number}, Reciter {reciter_id}. Status code: {res.status_code}")
            return {}
        
        data = res.json().get("timestamps", [])
        
        timestamps_map = {}
        for verse_data in data:
            verse_key = verse_data.get("verse_key")
            if verse_key and verse_data.get("segments"):
                timestamps_map[verse_key] = verse_data["segments"]
        
        TIMESTAMP_CACHE[key] = (timestamps_map, datetime.utcnow() + timedelta(hours=24))
        return timestamps_map

async def get_tafsir(ayah_key: str, tafsir_source: str):
    key = f"{ayah_key}:{tafsir_source}"
    if key in TAFSIR_CACHE:
        cached, expiry = TAFSIR_CACHE[key]
        if datetime.utcnow() < expiry:
            return cached
    async with httpx.AsyncClient() as client:
        tafsir_map = {"ibn_kathir": 1, "asadd": 20}
        tafsir_id = tafsir_map.get(tafsir_source, 1)
        res = await client.get(f"{BASE_URL}/tafsirs/by_ayah/{ayah_key}", params={"tafsir_id": tafsir_id})
        if res.status_code != 200:
            return None
        data = res.json().get("tafsir")
        TAFSIR_CACHE[key] = (data, datetime.utcnow() + timedelta(hours=1))
        return data

def list_reciters():
    return []

def get_audio(surah_number: int, reciter: str):
    return None

def extract_translation(verse: dict) -> str:
    verse_translation = "Translation data missing."
    
    if verse.get("translations") and isinstance(verse["translations"], list) and len(verse["translations"]) > 0:
        verse_translation = verse["translations"][0].get("text", "Translation not available.")
    
    if verse_translation in ["Translation data missing.", "Translation not available."]:
        word_translations = []
        for word in verse.get("words", []):
            word_text = word.get("translation", {}).get("text")
            if word_text and not word_text.startswith('(') and not word_text.endswith(')'):
                word_translations.append(word_text)
        
        if word_translations:
            verse_translation = " ".join(word_translations)
            
    return verse_translation

async def get_surah_list():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/chapters")
        if res.status_code != 200:
            return None
        return res.json().get("chapters")

async def get_surah_detail(
    surah_number: int,
    translation: str = "en.sahih",
    tafsir_sources: Optional[List[str]] = None,
    reciter: Optional[str] = None,
):
    
    async with httpx.AsyncClient() as client:
        surah_res = await client.get(f"{BASE_URL}/chapters/{surah_number}", params={"language": "en"})
        if surah_res.status_code != 200:
            return None
        surah = surah_res.json().get("chapter")
        
        reciter_base = reciter.replace('.mp3', '') if reciter else 'mishary_rashid'
        
        verses_res = await client.get(
            f"{BASE_URL}/verses/by_chapter/{surah_number}",
            params={
                "language": "en",
                "translations": translation,
                "limit": 300, 
                "words": True,
                "fields": "text_qpc_hafs", 
                "reciter": reciter_base
            },
        )
        
        if verses_res.status_code != 200:
            logging.error(f"API Error: Failed to fetch verses for Surah {surah_number}. Status code: {verses_res.status_code}")
            return None
        
        verses_json = verses_res.json()
        verses = verses_json.get("verses")
        
        surah_audio_url = get_audio(surah_number, reciter_base)
        
        timestamps_map = {}
        if reciter and surah_number != 1:
            timestamps_map = await get_timestamps(MISHARY_RECITER_ID, surah_number)
            
        for verse in verses:
            verse["translation"] = extract_translation(verse)
            
            verse["text_qpc_hafs"] = verse.get("text_qpc_hafs")

            ayah_key = verse["verse_key"]
            
            tafsir_data = []
            if tafsir_sources:
                for source in tafsir_sources:
                    data = await get_tafsir(ayah_key, source)
                    if data:
                        tafsir_data.append({"source": source.replace('_', ' ').title(), "text": data.get("text")})
            verse["tafsir"] = tafsir_data
            
            if reciter and surah_number != 1:
                if ayah_key in timestamps_map:
                    timestamps = timestamps_map[ayah_key]
                    words = verse.get("words", [])
                    
                    if len(timestamps) == len(words):
                        for i, word in enumerate(words):
                            segment = timestamps[i]
                            word["timing"] = {"start": segment[1], "end": segment[2]}
                        verse["words"] = words
                    else:
                        logging.warning(
                            f"Timestamp Mismatch for {ayah_key}: Words ({len(words)}) != Segments ({len(timestamps)}). Timing data will be missing for this verse."
                        )
                else:
                    logging.warning(
                        f"Missing Timestamp Entry for {ayah_key} in Surah {surah_number}. Timing data could not be applied."
                    )
                
        formatted_surah = {
            "id": surah.get("id"),
            "name_arabic": surah.get("name_arabic"),
            "name_simple": surah.get("name_simple"),
            "name_complex": surah.get("name_complex"),
            "name_translated": surah.get("translated_name", {}).get("name"),
            "revelation_place": surah.get("revelation_place"),
            "verses_count": surah.get("verses_count"),
            "bismillah": None, 
            "audio_url": surah_audio_url,
            "verses": verses,
        }
        
        return formatted_surah

async def get_page_detail(
    page_number: int,
    translation: str = "en.sahih",
    tafsir_sources: Optional[List[str]] = None,
    reciter: Optional[str] = None,
):
    
    reciter_base = reciter.replace('.mp3', '') if reciter else 'mishary_rashid'
    
    async with httpx.AsyncClient() as client:
        verses_res = await client.get(
            f"{BASE_URL}/verses/by_page/{page_number}",
            params={
                "language": "en",
                "translations": translation,
                "words": True,
                "fields": "text_qpc_hafs",
                "reciter": reciter_base
            }
        )
        
        if verses_res.status_code != 200:
            logging.error(f"API Error: Failed to fetch verses for Page {page_number}. Status code: {verses_res.status_code}")
            return None
            
        verses_json = verses_res.json()
        verses = verses_json.get("verses")
        
        if not verses:
            return {"verses": []}
            
        first_verse_key = verses[0]["verse_key"]
        surah_number = int(first_verse_key.split(":")[0])
        
        surah_res = await client.get(f"{BASE_URL}/chapters/{surah_number}", params={"language": "en"})
        surah = surah_res.json().get("chapter", {})

        surah_start_page = surah.get("pages", [page_number, page_number])[0]
        surah_end_page = surah.get("pages", [page_number, page_number])[1]

        surah_audio_url = get_audio(surah_number, reciter_base)
        
        timestamps_map = {}
        if reciter and surah_number != 1:
            timestamps_map = await get_timestamps(MISHARY_RECITER_ID, surah_number)
            
        for verse in verses:
            verse["translation"] = extract_translation(verse)
            verse["text_qpc_hafs"] = verse.get("text_qpc_hafs")

            ayah_key = verse["verse_key"]
            
            tafsir_data = []
            if tafsir_sources:
                for source in tafsir_sources:
                    data = await get_tafsir(ayah_key, source)
                    if data:
                        tafsir_data.append({"source": source.replace('_', ' ').title(), "text": data.get("text")})
            verse["tafsir"] = tafsir_data
            
            if reciter and surah_number != 1:
                if ayah_key in timestamps_map:
                    timestamps = timestamps_map[ayah_key]
                    words = verse.get("words", [])
                    
                    if len(timestamps) == len(words):
                        for i, word in enumerate(words):
                            segment = timestamps[i]
                            word["timing"] = {"start": segment[1], "end": segment[2]}
                        verse["words"] = words
                    else:
                        logging.warning(
                            f"Timestamp Mismatch for {ayah_key}: Words ({len(words)}) != Segments ({len(timestamps)}). Timing data will be missing for this verse."
                        )
                
        return {
            "surah_number": surah_number,
            "surah_name_arabic": surah.get("name_arabic"),
            "surah_name_simple": surah.get("name_simple"),
            "audio_url": surah_audio_url, 
            "verses": verses,
            "surah_start_page": surah_start_page,
            "surah_end_page": surah_end_page,
        }

async def get_ayah(
    ayah_key: str,
    tafsir_sources: Optional[List[str]] = None,
    reciter: Optional[str] = None,
):
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/verses/{ayah_key}", 
            params={
                "fields": "text_qpc_hafs",
                "translations": "en.sahih",
                "words": True
            }
        )
        if res.status_code != 200:
            return None
        
        verse = res.json().get("verse")
        surah_number = verse["chapter_id"]
        
        verse["translation"] = extract_translation(verse)
        verse["text_qpc_hafs"] = verse.get("text_qpc_hafs")
        
        tafsir_data = []
        if tafsir_sources:
            for source in tafsir_sources:
                data = await get_tafsir(ayah_key, source)
                if data:
                    tafsir_data.append({"source": source.replace('_', ' ').title(), "text": data.get("text")})
        verse["tafsir"] = tafsir_data

        if reciter:
            reciter_base = reciter.replace('.mp3', '')
            
            timestamps_map = await get_timestamps(MISHARY_RECITER_ID, surah_number)
            if ayah_key in timestamps_map:
                timestamps = timestamps_map[ayah_key]
                words = verse.get("words", [])
                
                if len(timestamps) == len(words):
                    for i, word in enumerate(words):
                        segment = timestamps[i]
                        word["timing"] = {"start": segment[1], "end": segment[2]}
                    verse["words"] = words
                    
        return verse

async def get_translation(lang: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/resources/translations", params={"language": lang})
        if res.status_code != 200:
            return None
        return res.json().get("translations")

async def search_quran(query: str, tafsir_source: Optional[str] = None):
    results = []
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/search", params={"q": query, "size": 100}) 
        if res.status_code != 200:
            return results
        hits = res.json().get("data", [])
        for hit in hits:
            ayah_key = hit["verse_key"]
            verse = await get_ayah(ayah_key, tafsir_sources=[tafsir_source] if tafsir_source else None)
            results.append(verse)
    return results