def type_conversion(prop_type):
    if prop_type.startswith("AN") or prop_type.startswith("enum_"):
        return "string"
    if prop_type == "GUID":
        return "string"
    if prop_type == "bedrag":
        return "number"
    
    return prop_type