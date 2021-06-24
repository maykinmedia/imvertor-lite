import json

from objects import Schema
from parsers import BaseParser
from utils import remove_keys_from_dict, lowercase_first_letter


class AmsterdamSchema(BaseParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attribute_blacklist = {
            "$ref",
            "license",
            "status",
            "version",
            "theme",
            "publisher",
            "owner",
            "authorizationGrantor",
            "keywords",
            "crs",
        }

    def process(self, file_name, encoding, **kwargs):
        """
        Process the Amsterdam Schema format (JSON)

        @param file_name: The name of the JSON file.
        @param encoding: The encoding of the given JSON file (Default: "utf-8").
        """

        with open(file_name, "r", encoding=encoding or "utf-8") as f:
            base_schema = json.load(f)

        clean_schema = remove_keys_from_dict(base_schema,
                                             ["id", "title", "type", "description", "tables"])

        base_schema = Schema(base_schema)

        schemas = base_schema.safe_pop("tables", default=[])
        for schema in schemas:
            schema = Schema(schema)
            schema["properties"] = schema.safe_pop("schema", {})
            schema["type"] = "object"

            for key in list(schema["properties"].keys()):
                if key not in ["properties"]:
                    schema[key] = schema["properties"].safe_pop(key)

            properties = schema["properties"].safe_pop("properties", {})
            for key, dic in properties.items():
                if key not in ["schema"]:
                    camelcase_key = lowercase_first_letter(key)

                    dic["$id"] = f"#/properties/{camelcase_key}"
                    dic["title"] = key
                    schema["properties"][camelcase_key] = self.filter_attributes(dic)

            if "schema" in schema["required"]:
                schema["required"].remove("schema")  # Remove "schema" property
            schema["description"] = schema.safe_pop("title")
            schema["title"] = schema.safe_pop("id")
            schema["id"] = f"https://github.com/open-objecten/objecttypes/{schema['title']}.json"

            schema.update(clean_schema)  # Update with aditional info found in base schema

            self.export_schema(schema)
