from src.shared import clean_string_number_from_non_digit_chars, parse_string_number_to_int, parse_string_number_to_int_optional, normalize_string_number

def normalize_string_number_correct_without_parsing_test():
  result = normalize_string_number( "12" )

  assert result == "12"

def normalize_string_number_correct_with_letters_without_parsing_test():
  result = normalize_string_number( "найдено 12" )

  assert result == "12"

def normalize_string_number_correct_with_parsing_test():
  result = normalize_string_number( "12", True )

  assert result == 12

def normalize_string_number_correct_with_letters_with_parsing_test():
  result = normalize_string_number( "найдено 12", True )

  assert result == 12


def normalize_string_number_wrong_without_parsing_test():
  result = normalize_string_number( "asd" )

  assert result == ""


def normalize_string_number_wrong_with_parsing_test():
  result = normalize_string_number( "asd", True )

  assert result == 0

def parse_string_number_to_int_optional_true_test():
  result = parse_string_number_to_int_optional( "12", True )

  assert result == 12

def parse_string_number_to_int_optional_false_test():
  result = parse_string_number_to_int_optional( "12", False )

  assert result == "12"

def parse_string_number_to_int_optional_default_test():
  result = parse_string_number_to_int_optional( "12" )

  assert result == "12"

def parse_string_number_to_int_normal_test():
  result = parse_string_number_to_int( "12" )

  assert result == 12

def parse_string_number_to_int_empty_test():
  result = parse_string_number_to_int( "" )

  assert result == 0

def clean_string_number_from_non_digit_chars_normal_test():
  result = clean_string_number_from_non_digit_chars( "1231" )

  assert result == "1231"

def clean_string_number_from_non_digit_chars_with_text_test():
  result = clean_string_number_from_non_digit_chars( "найдено 1231" )

  assert result == "1231"

def clean_string_number_from_non_digit_chars_empty_test():
  result = clean_string_number_from_non_digit_chars( "" )

  assert result == ""