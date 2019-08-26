import os

def _safe_load(var):
    if os.getenv(var):
        return os.getenv(var)
    else:
        raise EnvironmentError(f"The `{var}` environment variable does not exist.")

class ConfigLoader(object):

    API_ENDPOINT = _safe_load('API_ENDPOINT')
