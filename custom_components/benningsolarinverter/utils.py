def is_number_type(type: str | None) -> bool:
    """
    Returns whether the given type string is a number type.
    The API always returns a value type as a string, that corresponds to the type that the "val" attribute is.
    """

    if type == None:
        return False

    return type in ["F", "L", "i", "w", "b"];


def parse_number(data) -> str | float:
    """
    Will parse the given data response from the API to a string or float, depending on the response.
    """

    value: str | float = data["val"]

    if not is_number_type(data["type"]):
        return value

    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value

    factor = data["factor"]

    if isinstance(factor, str):
        try:
            factor = float(factor)
        except ValueError:
            return value

    return value * factor;
