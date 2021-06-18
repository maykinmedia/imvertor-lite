import re
from typing import List, Dict


def isfloat(string):
    if re.match(r'^-?\d+(?:\.\d+)$', string):
        return True


def type_conversion(prop_type: str):
    if not prop_type or not isinstance(prop_type, str):
        return None

    if prop_type.startswith("AN") or prop_type.startswith("enum_"):
        return "string"
    if prop_type == "GUID":
        return "string"
    if prop_type == "bedrag":
        return "number"
    if prop_type.isdigit():
        return int(prop_type)
    if isfloat(prop_type):
        return float(prop_type)
    if prop_type.lower() in ["false", "true"]:
        return eval(prop_type.title())

    return prop_type


def type_convert_dictionary(dictionary: Dict):
    return {k: type_conversion(v) for k, v in dictionary.items()}


def filter_list_duplicates(input_list: List):
    return list(dict.fromkeys(input_list))
