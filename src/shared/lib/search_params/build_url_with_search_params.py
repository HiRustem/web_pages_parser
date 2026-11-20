import re

URL_HAS_SEARCH_PARAMS_REGEXP = r"\?(?:[^#]*)"

def build_search_url( url, search_params=None ):
  search_params_string = build_search_params_string( search_params )
  separator = get_search_params_separator( url )

  if not search_params_string:
    return url
  
  return f"{url}{separator}{search_params_string}"

def build_search_params_string( search_params=None ):
  if not search_params or len(search_params.items()) == 0:
    return ""
  
  result_string = ""

  for key, value in search_params.items():
    if result_string:
      result_string += "&"

    result_string += f"{key}={value}"

  return result_string

def get_search_params_separator( url ):
  return "&" if has_search_params( url ) else "?"

def has_search_params( url ):
  return bool(re.search( URL_HAS_SEARCH_PARAMS_REGEXP, url ))