from typing import Dict

from settings import ATTRIBUTE_BLACKLIST


class BaseParser:

    @staticmethod
    def filter_attributes(attrs: Dict):
        return {k: v for k, v in attrs.items() if k not in ATTRIBUTE_BLACKLIST}
