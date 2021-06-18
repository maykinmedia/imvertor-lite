import json
from typing import Dict

from settings import ATTRIBUTE_BLACKLIST


class BaseParser:

    @staticmethod
    def filter_attributes(attrs: Dict):
        return {k: v for k, v in attrs.items() if k not in ATTRIBUTE_BLACKLIST}

    @staticmethod
    def export_schema_as_json(schema: Dict, filename: str):
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)

    @staticmethod
    def write_readme_template(schema: Dict, template_name: str, filename: str):
        ...
