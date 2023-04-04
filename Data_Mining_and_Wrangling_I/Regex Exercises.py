import re

def is_date(test_str):
    """
    Return True if test_str is a valid date based on the given date format.
    """

    return bool(re.match('^\d{4}[\-/]\d{2}[\-/]'
                         '\d{2}$|^\d{2}[\-/]\d{2}[\-/]\d{4}$', test_str))

def find_data(text):
    """
    Returns all occurences of "data set" or "dataset"
    in text as a list of strings.
    """

    return re.findall(r'\bdata ?set\b', text)

def find_lamb(text):
    """
    Returns all phrases in text that being with the word "little" and end
    with the word "lamb" as a list of strings.
    """

    return re.findall(r'\blittle [a-zA-Z. ]* lamb\b|\blittle lamb\b', text)

def repeat_alternate(text):
    """
    Returns a string where every other word of text is repeated.
    """

    return re.sub("(\w+'?\w? )(\w+'?\w?)", r"\1\1\2", text)

def whats_on_the_bus(text):
    """
    Returns the unique items that are on the bus according to the text.
    """

    return set(re.findall(r'\w+(?= on the bus)', text))

def to_list(text):
    """
    Returns the list of items in text which were delimited by
    ",", "+" or "and".
    """

    return re.split(',|\+|and', text)

def march_product(text):
    """
    Returns the product of each "m by n" pair in text.
    """

    return [int(mp[0]) * int(mp[1]) 
            for mp in re.findall(r'(\d+) by (\d+)', text)]

def get_big(items):
    """
    Takes in list of items and returns the list of "ITEMs"
    that begin with "Big" but with an SKU that is not all numbers.
    """

    return re.findall(r'(?<=[0-9][A-Z] |[A-Z][0-9] )Big .*', items)

def find_chris(names):
    """
    Aceppts list of names as input and returns a list of all first names in
    "names" that contain the case-insensitive string "Chris" but with a last
    name that doesn't start with "B" or "M".
    """

    return re.findall(r' (\w*[Cc]hris\w*) [^BMbm]', names)

def get_client(server_log):
    """
    Read server_log and returns the client IP, date/time of server access
    and status code. The ouput is a list of tuples.
    """

    return re.findall(r'(\d+\.\d+\.\d+\.\d+).*\[(.*)\].*1" (\d+).*', server_log)

