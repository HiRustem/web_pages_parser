import re

STRING_NUMBER_ONLY_DIGITS_REGEXP = r"\D"

def normalize_string_number( string_number=None, parse_to_int=False ):
  if not string_number or len(string_number) == 0:
    return parse_string_number_to_int_optional( "", parse_to_int )
  
  clean_string_number = clean_string_number_from_non_digit_chars( string_number )

  if not clean_string_number:
    return parse_string_number_to_int_optional( "", parse_to_int )
  
  return parse_string_number_to_int_optional( clean_string_number, parse_to_int )
  

def parse_string_number_to_int_optional( string_number, parse_to_int=False ):
  if parse_to_int:
    return parse_string_number_to_int( string_number )
  
  return string_number

def parse_string_number_to_int( string_number ):
  try:
    return int( string_number )
  except ValueError:
    return 0

def clean_string_number_from_non_digit_chars( string_number ):
  return re.sub( STRING_NUMBER_ONLY_DIGITS_REGEXP, "", string_number )

