"""
Cache management for MasterBus.

Implements the hybrid cache invalidation strategy as defined in Advisory 003.
"""
import json
import redis
import os
import logging
from typing import Any, Dict, Optional, Union, List
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching of calculation results and other data using Redis.
    
    Implements a hybrid invalidation strategy:
    - Time-based expiration
    - Event-based invalidation
    - Versioned cache keys
    - Soft invalidation for stale data
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the cache manager.
        
        Args:
            redis_url: Redis connection URL. Defaults to environment variable.
        """
        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.from_url(url, decode_responses=True)
        self.version = os.getenv("RISK_ALGORITHM_VERSION", "1.0")
        
        # Default TTLs
        self.default_ttl = timedelta(hours=24)
        self.aggregate_ttl = timedelta(hours=1)
    
    def _build_key(self, key_type: str, resource_id: str) -> str:
        """
        Build a versioned cache key.
        
        Args:
            key_type: Type of data being cached (e.g., "risk", "compliance")
            resource_id: ID of the resource (e.g., equipment_id, facility_id)
            
        Returns:
            Formatted cache key string
        """
        return f"{key_type}:v{self.version}:{resource_id}"
    
    def get(self, key_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache.
        
        Args:
            key_type: Type of data to retrieve
            resource_id: ID of the resource
            
        Returns:
            Cached data or None if not found
        """
        key = self._build_key(key_type, resource_id)
        data = self.redis.get(key)
        
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in cache for key {key}")
                return None
        return None
    
    def set(
        self, 
        key_type: str, 
        resource_id: str, 
        data: Dict[str, Any], 
        ttl: Optional[timedelta] = None
    ) -> bool:
        """
        Store data in cache.
        
        Args:
            key_type: Type of data to store
            resource_id: ID of the resource
            data: Data to cache
            ttl: Time-to-live (defaults to default_ttl)
            
        Returns:
            True if successful
        """
        key = self._build_key(key_type, resource_id)
        expiry = ttl or self.default_ttl
        
        try:
            serialized = json.dumps(data)
            return bool(self.redis.setex(key, int(expiry.total_seconds()), serialized))
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Failed to cache data for {key}: {str(e)}")
            return False
    
    def invalidate(self, key_type: str, resource_id: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            key_type: Type of data to invalidate
            resource_id: ID of the resource
            
        Returns:
            True if successful
        """
        key = self._build_key(key_type, resource_id)
        return bool(self.redis.delete(key))
    
    def invalidate_facility(self, facility_id: str) -> bool:
        """
        Invalidate all cache entries for a facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            True if successful
        """
        # Invalidate facility-level caches
        self.invalidate("risk", f"facility:{facility_id}")
        self.invalidate("compliance:nfpa70b", f"facility:{facility_id}")
        self.invalidate("compliance:nfpa70e", f"facility:{facility_id}")
        
        # Could be expanded to invalidate equipment within the facility
        return True
    
    def invalidate_equipment(self, equipment_id: str, facility_id: Optional[str] = None) -> bool:
        """
        Invalidate cache for equipment and propagate to facility.
        
        Args:
            equipment_id: Equipment ID
            facility_id: Optional facility ID for propagation
            
        Returns:
            True if successful
        """
        # Invalidate equipment cache
        success = self.invalidate("risk", f"equipment:{equipment_id}")
        
        # Propagate invalidation up to facility if provided
        if facility_id:
            self.invalidate_facility(facility_id)
            
        return success
    
    def mark_stale(self, key_type: str, resource_id: str) -> bool:
        """
        Mark a cache entry as stale but keep it available.
        
        Args:
            key_type: Type of data to mark stale
            resource_id: ID of the resource
            
        Returns:
            True if successful
        """
        key = self._build_key(key_type, resource_id)
        data = self.redis.get(key)
        
        if not data:
            return False
            
        try:
            parsed = json.loads(data)
            parsed["_stale"] = True
            parsed["_stale_since"] = self.redis.time()[0]  # Current server time
            return bool(self.redis.set(key, json.dumps(parsed)))
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to mark data as stale for {key}: {str(e)}")
            return False 