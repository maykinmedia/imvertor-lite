import json

from parsers import BaseParser


class AmsterdamSchema(BaseParser):

    @staticmethod
    def process(file_name, encoding, **kwargs):
        """
        Process the Amsterdam Schema format (JSON)

        @param file_name: The name of the JSON file.
        @param encoding: The encoding of the given JSON file (Default: "utf-8").
        """

        with open(file_name, "r", encoding=encoding if encoding else "utf-8") as f:
            obj = json.load(f)

        schemas = obj["tables"]
        for schema in schemas:
            schema["properties"] = schema.pop("schema")
            schema["type"] = "object"

            for key in list(schema["properties"].keys()):
                if key not in ["properties"]:
                    schema[key] = schema["properties"].pop(key)

            properties = schema["properties"].pop("properties")
            for key, dic in properties.items():
                if key not in ["schema"]:
                    dic["$id"] = f"#/properties/{key}"
                    dic["title"] = key
                    schema["properties"][key] = dic

            schema["required"].remove("schema")  # Remove "schema" property

            with open(f"{schema['title'].lower()}.json", "w") as f:
                json.dump(schema, f, indent=2)
