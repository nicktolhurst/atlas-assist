
import re
import string


def extract_search_term(input, regex): 
    try:
        r = re.compile(regex, re.IGNORECASE)
        match = re.search(r, input)
        
        if not match:
            return None, None
        
        search_term = match.group(2).strip().rstrip(string.punctuation)
        
        return search_term
        
    except Exception as e:
        return None
