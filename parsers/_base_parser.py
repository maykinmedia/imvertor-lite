import json
from typing import Dict


class BaseParser:

    def __init__(self, readme_template=None):
        self.readme_template = readme_template
        self.schema_title_key = "title"
        self.attribute_blacklist = set()

    def filter_attributes(self, attrs):
        return {k: v for k, v in attrs.items() if k not in self.attribute_blacklist}

    def get_schema_title(self, schema):
        return schema[self.schema_title_key].lower()

    def export_schema_as_json(self, schema: Dict):
        schema = self.filter_attributes(schema)
        with open(f"{self.get_schema_title(schema)}.json", "w") as f:
            json.dump(schema, f, indent=2)

    def write_readme_template(self, schema: Dict):
        with open(self.readme_template, "r") as f:
            data = f.read()

        for key, val in schema.items():
            data = data.replace("{{%s}}" % key, str(val))

        with open(f"{self.get_schema_title(schema)}.md", "w") as f:
            f.write(data)

    def export_schema(self, schema):
        self.export_schema_as_json(schema)

        if self.readme_template:
            self.write_readme_template(schema)
