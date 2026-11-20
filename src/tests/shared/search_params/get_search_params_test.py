from src.shared import get_search_params, parse_url, parse_url_query

TEST_SEARCH_PARAMS_WHITELIST = ["q"]
TEST_URL_WITHOUT_SEARCH_PARAMS = "https://example.com"
TEST_URL_WITH_SEARCH_PARAMS = "https://example.com?q=python&page=1"

def test_get_search_params_without_whitelist():
  result = get_search_params( TEST_URL_WITH_SEARCH_PARAMS )

  assert result == {
    "q": "python",
    "page": "1"
  }

def test_get_search_params_with_whitelist():
  result = get_search_params(TEST_URL_WITH_SEARCH_PARAMS, TEST_SEARCH_PARAMS_WHITELIST)

  assert result == {
    "q": "python"
  }

def test_get_search_params_without_search_params():
  result = get_search_params(TEST_URL_WITHOUT_SEARCH_PARAMS)

  assert result == {}


def test_parse_url():
  result = parse_url( TEST_URL_WITH_SEARCH_PARAMS ).query

  assert result == "q=python&page=1"

def test_parse_url_without_search_params():
  result = parse_url( TEST_URL_WITHOUT_SEARCH_PARAMS ).query

  assert result == ""
  

def test_parse_url_query():
  result = parse_url_query( TEST_URL_WITH_SEARCH_PARAMS )

  assert result == {"https://example.com?q": ["python"], "page": ["1"]}

def test_parse_url_query_without_search_params():
  result = parse_url_query( TEST_URL_WITHOUT_SEARCH_PARAMS )

  assert result == {}
