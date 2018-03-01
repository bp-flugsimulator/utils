"""
This module contains function to check the type of variables.
"""


def ensure_type(name, var, *types):
    """
    Checks if a variable with a name has one of the allowed types.

    Arguments
    ---------
        name: variable name
        var: python object
        *types: allowed types
    """
    for ty in types:
        if not isinstance(ty, type):
            raise ValueError(
                "The given value {} in *types is not a type. (found {})".
                format(ty, type(ty).__name__))

        if isinstance(var, ty):
            return

    raise TypeError("{} has to be {}. (found {})".format(
        name,
        ' or'.join(map(lambda x: x.__name__, types)),
        type(var).__name__,
    ))


def ensure_type_array(name, array, *types):
    """
    Checks if one type holds for all array elements.

    Arguments
    ---------
        name: variable name
        var: array with python objects
        *types: allowed types
    """
    for ty in types:
        if not isinstance(ty, type):
            raise ValueError(
                "The given value {} in *types is not a type. (found {})".
                format(ty, type(ty).__name__))

    errors = []

    for idx, var in enumerate(array):
        skip = False
        for ty in types:
            if isinstance(var, ty):
                skip = True
                break
        if skip:
            continue
        else:
            errors.append((idx, type(var)))

    if errors:
        raise TypeError(
            "All elements in {} has to be {}. This does not hold for the elements:\n{}".
            format(
                name,
                ' or'.join(map(lambda x: x.__name__, types)),
                '\n'.join(
                    map(lambda e: "\telement with index " + str(e[0]) + " has type " + str(e[1].__name__),
                        errors)),
            ))
