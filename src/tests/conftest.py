import pytest
from src.app import AppContext, get_site_config, setup_logging

site_key = "hh"

@pytest.fixture
def test_context():
  config = get_site_config( site_key )
  logger = setup_logging()
  return AppContext(config=config, logger=logger)