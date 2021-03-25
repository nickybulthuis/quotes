import re

import unicodedata


def remove_accents(input_str):
    return u''.join([c for c in unicodedata.normalize('NFKD', input_str) if not unicodedata.combining(c)])


def clean_fund_name(input_str):
    return re.sub(r'[\s€%&()+-]+', '-', str.lower(remove_accents(input_str)))
