from src.app import AppContext, get_site_config, setup_logging

site_key = "hh"

def run(site_key: str):
  config = get_site_config(site_key)
  logger = setup_logging()

  ctx = AppContext(
    config = config, 
    logger = logger
  )

run( site_key )