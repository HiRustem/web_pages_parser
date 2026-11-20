from src.shared import has_search_params, get_search_params_separator, build_search_params_string, build_search_url

TEST_URL_WITHOUT_SEARCH_PARAMS = "https://example.com"
TEST_URL_WITH_SEARCH_PARAMS = "https://example.com?q=python&page=1"
TEST_URL_SEARCH_PARAMS_OBJECT = {
  "group": "all",
  "sort": "all"
}

def test_build_search_url_with_url_params_and_search_params():
  result = build_search_url( TEST_URL_WITH_SEARCH_PARAMS, TEST_URL_SEARCH_PARAMS_OBJECT )

  assert result == "https://example.com?q=python&page=1&group=all&sort=all"

def test_build_search_url_with_url_params_and_no_search_params():
  result = build_search_url( TEST_URL_WITH_SEARCH_PARAMS )

  assert result == "https://example.com?q=python&page=1"

def test_build_search_url_with_url_no_params_and_search_params():
  result = build_search_url( TEST_URL_WITHOUT_SEARCH_PARAMS, TEST_URL_SEARCH_PARAMS_OBJECT )

  assert result == "https://example.com?group=all&sort=all"

def test_build_search_url_with_url_no_params_and_no_search_params():
  result = build_search_url( TEST_URL_WITHOUT_SEARCH_PARAMS )

  assert result == "https://example.com"

def test_build_search_params_string():
  result = build_search_params_string( TEST_URL_SEARCH_PARAMS_OBJECT )

  assert result == "group=all&sort=all"

def test_build_search_params_string_no_params():
  result = build_search_params_string()

  assert result == ""

def test_build_search_params_string_empty_params_object():
  result = build_search_params_string( {} )

  assert result == ""

def test_get_search_params_separator_no_params():
  result = get_search_params_separator( TEST_URL_WITHOUT_SEARCH_PARAMS )

  assert result == "?"

def test_get_search_params_separator():
  result = get_search_params_separator( TEST_URL_WITH_SEARCH_PARAMS )

  assert result == "&"


def test_has_search_params_no_params():
  result = has_search_params( TEST_URL_WITHOUT_SEARCH_PARAMS )

  assert result == False


def test_has_search_params():
  result = has_search_params( TEST_URL_WITH_SEARCH_PARAMS )

  assert result == True
