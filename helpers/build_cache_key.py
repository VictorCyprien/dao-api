from api.views.daos.dao_view_handler import DaoViewHandler


def make_token_key(*args, method="GET", **kwargs) -> str:
    """
    Generate a cache key for token data.
    """
        # Handle both positional and keyword arguments
    if len(args) > 1 and isinstance(args[0], DaoViewHandler):
        # Class-based view: args[0] is 'self', args[1] is dao_id
        dao_id = args[1]
    elif 'dao_id' in kwargs:
        # Either function-based view or params passed as keywords
        dao_id = kwargs['dao_id']
    else:
        # Fallback
        dao_id = "unknown"

    return f"token_{dao_id}"


def make_treasury_key(*args, method="GET", **kwargs) -> str:
    """
    Generate a cache key for treasury data.
    
    For class-based views:
      - args[0] will be 'self' (the class instance)
      - args[1] will be the first route parameter (dao_id in this case)
      
    For function views:
      - args[0] would be the first route parameter
      
    For both, kwargs may contain route parameters by name
    
    Args:
        *args: Positional arguments passed to the view
        method: HTTP method (GET, PUT, POST, etc.) - defaults to "GET"
        **kwargs: Keyword arguments passed to the view
    """
    # Handle both positional and keyword arguments
    if len(args) > 1 and isinstance(args[0], DaoViewHandler):
        # Class-based view: args[0] is 'self', args[1] is dao_id
        dao_id = args[1]
    elif 'dao_id' in kwargs:
        # Either function-based view or params passed as keywords
        dao_id = kwargs['dao_id']
    else:
        # Fallback
        dao_id = "unknown"
    
    # Use different cache keys for different HTTP methods
    return f"treasury_dao_{dao_id}_{method}"
