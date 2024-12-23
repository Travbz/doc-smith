from typing import Optional, Any, Dict
import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from ...utils.logging_config import setup_logger
from ....config.settings import CACHE_DIR, CACHE_TTL, CACHE_ENABLED

logger = setup_logger(__name__)

class CacheManager:
    def __init__(self, cache_dir: Path = CACHE_DIR, ttl: int = CACHE_TTL):
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if not CACHE_ENABLED:
            return None
            
        try:
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                return None
                
            # Check if cache is expired
            if self._is_expired(cache_file):
                self.delete(key)
                return None
                
            with cache_file.open('rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {str(e)}")
            return None
            
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        if not CACHE_ENABLED:
            return
            
        try:
            cache_file = self._get_cache_file(key)
            with cache_file.open('wb') as f:
                pickle.dump(value, f)
                
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {str(e)}")
            
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        try:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
                
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {str(e)}")
            
    def clear(self) -> None:
        """Clear all cached values."""
        try:
            for cache_file in self.cache_dir.glob('*.cache'):
                cache_file.unlink()
                
        except Exception as e:
            logger.warning(f"Cache clear failed: {str(e)}")
            
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key."""
        # Create a hash of the key to use as filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
        
    def _is_expired(self, cache_file: Path) -> bool:
        """Check if a cache file is expired."""
        if not self.ttl:
            return False
            
        modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return datetime.now() - modified_time > timedelta(seconds=self.ttl)
        
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return hashlib.sha256(":".join(key_parts).encode()).hexdigest()

# Create singleton instance
cache_manager = CacheManager()