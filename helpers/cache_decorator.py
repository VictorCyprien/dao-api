from functools import wraps
from typing import Callable, Optional, Any

from flask import request
from api.app import cache


def cached_view(timeout: int = 1800, key_prefix: str = None, make_key: Callable = None):
    """
    A decorator that caches the result of a view function for a specified time.
    
    Args:
        timeout: Cache timeout in seconds (default: 30 minutes)
        key_prefix: A custom prefix for the cache key
        make_key: A custom function to generate a cache key based on function arguments
                  Function signature should be make_key(*args, **kwargs) -> str
    
    Usage:
        @cached_view(timeout=3600)
        def my_view_function(id):
            # This result will be cached for 1 hour
            return expensive_database_query(id)
            
        @cached_view(key_prefix="user_profile")
        def get_user(user_id):
            # Custom key prefix
            return user_data

        @cached_view(make_key=lambda user_id, **kwargs: f"custom_user_{user_id}")
        def get_user_custom(user_id):
            # Fully custom key generation
            return user_data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if make_key:
                # Use custom key generator if provided
                # Pass both args and kwargs to the key maker
                cache_key = make_key(*args, **kwargs)
            else:
                # Default key generation: function name + args + relevant part of request
                if key_prefix:
                    prefix = key_prefix
                else:
                    prefix = f"{func.__module__}.{func.__name__}"
                
                # Extract the parameters from the route that might be relevant
                view_args = request.view_args.copy() if hasattr(request, 'view_args') else {}
                
                # Create a cache key from the prefix and the arguments
                # For class methods, skip the first argument (self)
                start_idx = 1 if args and not isinstance(args[0], (str, int, float, bool)) else 0
                arg_parts = [f"{arg}" for arg in args[start_idx:] if isinstance(arg, (str, int, float, bool))]
                
                # Combine kwargs and view_args, but skip 'self' 
                kwarg_parts = [f"{k}={v}" for k, v in {**kwargs, **view_args}.items() 
                               if k != 'self' and isinstance(v, (str, int, float, bool))]
                
                all_parts = arg_parts + kwarg_parts
                cache_key = f"{prefix}:{':'.join(all_parts)}" if all_parts else prefix
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # If not in cache, call the function
            result = func(*args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_view_cache(key_pattern: str = None, exact_key: str = None, make_key: Callable = None, *args, **kwargs):
    """
    Invalidate a specific cache entry or pattern
    
    Args:
        key_pattern: Pattern to match against cache keys (uses substring match)
        exact_key: Exact cache key to invalidate
        make_key: Function to generate the exact key (same as used in cached_view)
        *args, **kwargs: Arguments to pass to make_key if provided
    """
    if make_key:
        # Use the same key generator as cached_view
        key = make_key(*args, **kwargs)
        cache.delete(key)
    elif exact_key:
        # Delete an exact key
        cache.delete(exact_key)
    elif key_pattern:
        # This part is implementation-specific
        # Some cache backends don't support pattern-based deletion
        try:
            # For Redis cache, we can use the delete_pattern method if available
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"*{key_pattern}*")
            else:
                # For other backends, we would need a different approach
                # This is a placeholder that would need to be adapted based on your cache backend
                pass
        except Exception as e:
            # Log the error but don't crash
            print(f"Error invalidating cache pattern {key_pattern}: {e}")
    else:
        # No key specified, do nothing
        pass 