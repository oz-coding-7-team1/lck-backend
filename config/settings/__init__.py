from .base import *

environment = 'dev'

if environment == 'prod':
    from .prod import *
elif environment == 'dev':
    from .dev import *
else:
    raise ValueError(f"Invalid environment: {environment}")