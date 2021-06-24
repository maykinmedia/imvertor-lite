import json
import os
from typing import Dict


class BaseParser:

    def __init__(self, readme_template=None, postfix=None):
        self.readme_template = readme_template
        self.schema_title_key = "title"
        self.attribute_blacklist = set()
        self.postfix = ""

        if postfix:
            self.postfix = f"-{postfix}"

    def filter_attributes(self, attrs):
        return {k: v for k, v in attrs.items() if k not in self.attribute_blacklist}

    def get_schema_title(self, schema):
        return schema[self.schema_title_key].lower()

    def export_schema_as_json(self, schema: Dict, title: str):
        with open(f"{title}/{title}{self.postfix}.json", "w") as f:
            json.dump(schema, f, indent=2)

    def write_readme_template(self, schema: Dict, title: str):
        with open(self.readme_template, "r") as f:
            data = f.read()

        for key, val in schema.items():
            data = data.replace("{{%s}}" % key, str(val))

        with open(f"{title}/README{self.postfix}.md", "w") as f:
            f.write(data)

    def export_schema(self, schema):
        title = self.get_schema_title(schema)

        if not os.path.isdir(title):
            os.mkdir(title)

        if self.readme_template:
            self.write_readme_template(schema, title)

        schema = self.filter_attributes(schema)
        self.export_schema_as_json(schema, title)
