import urllib.parse as url_parser

def get_search_params( url, search_params_whitelist=None ):
  return create_search_params_object( 
    parse_url_query( 
      parse_url( url ).query 
    ),
    search_params_whitelist
  )

def parse_url( url ):
  return url_parser.urlparse( url )

def parse_url_query( query ):
  return url_parser.parse_qs( query )

def create_search_params_object( parsed_url_query, search_params_whitelist=None ):
  result = {}
  items = parsed_url_query.items()

  for key, value in items:
    if not search_params_whitelist:
      result[key] = value[0]
      continue

    if key in search_params_whitelist:
      result[key] = value[0]
  
  return result