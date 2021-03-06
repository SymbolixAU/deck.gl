import json


def to_camel_case(snake_case):
    """Makes a snake case string into a camel case one

    Parameters
    -----------
    snake_case : str
        Snake-cased string (e.g., "snake_cased") to be converted to camel-case (e.g., "camelCase")
    """
    output_str = ''
    should_upper_case = False
    for c in snake_case:
        if c == '_':
            should_upper_case = True
            continue
        output_str = output_str + c.upper() if should_upper_case else output_str + c
        should_upper_case = False
    return output_str


def lower_first_letter(s):
    return s[:1].lower() + s[1:] if s else ''


def lower_camel_case_keys(attrs):
    """Makes all the keys in a dictionary camel-cased and lower-case

    Parameters
    ----------
    attrs : dict
        Dictionary for which all the keys should be converted to camel-case
    """
    for snake_key in list(attrs.keys()):
        if '_' not in snake_key:
            continue
        camel_key = lower_first_letter(to_camel_case(snake_key))
        attrs[camel_key] = attrs.pop(snake_key)


def default_serialize(o, remap_function=lower_camel_case_keys):
    """Default method for rendering JSON from a dictionary"""
    attrs = vars(o)
    attrs = {k: v for k, v in attrs.items() if v is not None}
    if attrs.get('deck_widget'):
        del attrs['deck_widget']
    if remap_function:
        remap_function(attrs)
    return attrs


def serialize(serializable):
    """Takes a serializable object and JSONifies it"""
    return json.dumps(serializable, sort_keys=True, default=default_serialize)


class JSONMixin(object):

    def __repr__(self):
        """
        Override of string representation method to return a JSON-ified version of the
        Deck object.
        """
        return serialize(self)

    def to_json(self):
        """
        Return a JSON-ified version of the Deck object.
        """
        return serialize(self)
