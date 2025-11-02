"""
Caching utilities for Finnish Learning API
Implements in-memory and file-based caching to speed up responses
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

class WordCache:
    """In-memory cache with file persistence for word lookups"""
    
    def __init__(self, cache_dir='cache', ttl_hours=24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live in hours (default 24)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.ttl = timedelta(hours=ttl_hours)
        
    def _get_cache_key(self, word, source_lang, target_lang):
        """Generate cache key from word and languages"""
        key_str = f"{word}_{source_lang}_{target_lang}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, word, source_lang='fi', target_lang='da'):
        """
        Get cached word data
        
        Returns:
            dict or None: Cached data if found and valid, None otherwise
        """
        cache_key = self._get_cache_key(word, source_lang, target_lang)
        
        # Check memory cache first (fastest)
        if cache_key in self.memory_cache:
            data, timestamp = self.memory_cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                # Expired, remove from memory
                del self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                # Check expiry
                cached_time = datetime.fromisoformat(cached['cached_at'])
                if datetime.now() - cached_time < self.ttl:
                    # Load into memory cache
                    self.memory_cache[cache_key] = (cached['data'], cached_time)
                    return cached['data']
                else:
                    # Expired, delete file
                    cache_file.unlink()
            except Exception:
                # Corrupted cache file, delete it
                cache_file.unlink()
        
        return None
    
    def set(self, word, data, source_lang='fi', target_lang='da'):
        """
        Cache word data
        
        Args:
            word: The word to cache
            data: The word data to cache
            source_lang: Source language
            target_lang: Target language
        """
        cache_key = self._get_cache_key(word, source_lang, target_lang)
        now = datetime.now()
        
        # Store in memory
        self.memory_cache[cache_key] = (data, now)
        
        # Store in file
        cache_file = self._get_cache_file(cache_key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'word': word,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'cached_at': now.isoformat(),
                    'data': data
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to write cache file: {e}")
    
    def clear(self, word=None, source_lang='fi', target_lang='da'):
        """
        Clear cache
        
        Args:
            word: Specific word to clear, or None to clear all
        """
        if word:
            # Clear specific word
            cache_key = self._get_cache_key(word, source_lang, target_lang)
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
    
    def stats(self):
        """Get cache statistics"""
        file_count = len(list(self.cache_dir.glob("*.json")))
        return {
            'memory_cache_size': len(self.memory_cache),
            'file_cache_size': file_count,
            'cache_dir': str(self.cache_dir)
        }
