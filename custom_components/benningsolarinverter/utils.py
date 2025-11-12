import logging
import json

_LOGGER = logging.getLogger(__name__)

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

    _LOGGER.debug("Trying to parse value: " + json.dumps(data))

    value: str | float = data["val"]

    if not is_number_type(data["type"]):
        _LOGGER.debug("The given type variable does not indicate the variable is a number type! Will just return the value itself.")
        return value

    if isinstance(value, str):
        _LOGGER.debug("The given value is a string! Will try to parse as float.")
        try:
            value = float(value)
        except ValueError:
            _LOGGER.debug("Error while trying to parse the value as float, it seemingly is no number. We will just return the number!")
            return value

    factor = data["factor"]

    if isinstance(factor, str):
        _LOGGER.debug("The given factor is a string! Will try to parse as float.")
        try:
            factor = float(factor)
        except ValueError:
            _LOGGER.debug("Error while trying to parse the factor as float, it seemingly is no number. We will just return the value!")
            return value

    result_value = value * factor

    _LOGGER.debug("Successfully calculated result value: " + str(result_value))

    return result_value
