import json
import random

from bs4 import BeautifulSoup, ResultSet, Tag
import cchardet

from parsers import BaseParser
from utils import type_convert_dictionary, type_conversion, filter_list_duplicates


class EnterpriseArchitect(BaseParser):

    @staticmethod
    def get_initial_value(element: Tag):
        initial = element.select_one("initial").get("body")
        if initial:
            return initial
        else:
            return None

    @staticmethod
    def get_example(attr_type):
        """Set an example on the base schema based on the attribute type."""
        if attr_type == "string":
            return random.choice(["foo", "bar", "baz"])
        elif attr_type == "boolean":
            return random.choice([True, False])
        elif attr_type == "integer":
            return random.randint(1, 100)
        elif attr_type == "number":
            return random.uniform(1, 100)

    def extract_properties(self, attr: Tag):
        attr_name = attr.get("name")
        attr_dict = {
            "$id": f"#/properties/{attr_name}",
            "title": f"{attr_name}",
        }

        attr_props = attr.select_one("properties")
        attr_dict.update(attr_props.attrs)

        initial_value = self.get_initial_value(attr)
        if initial_value:
            attr_dict["default"] = type_conversion(initial_value)

        attr_type = attr_props.get("type")
        if attr_type:
            attr_dict["type"] = type_conversion(attr_type)

        stereotype = attr.select_one("stereotype")
        if stereotype:
            attr_dict["stereotype"] = stereotype.get('stereotype')

        documentation = attr.select_one("documentation")
        if documentation:
            attr_dict["description"] = documentation.get("value")

        tags = attr.select_one("tags").select("tag")
        if tags:
            attr_dict["tags"] = [{"name": tag.get("name"),
                                  "value": tag.get("value"),
                                  "notes": tag.get("notes")} for tag in tags]

        return attr_dict

    def process(self, file_name, class_name, encoding, **kwargs):
        """
        Process the Enteprise Architect format (XML)

        @param file_name: The name of the XML file.
        @param class_name: The base UML class name.
        @param encoding: The encoding of the given XML file (Default: "latin-1").
        """

        with open(file_name, "r", encoding=encoding if encoding else "latin-1") as f:
            data = f.read()

        soup = BeautifulSoup(data, "lxml")

        if class_name:
            base_list = soup.find_all("element", {"xmi:type": "uml:Class", "name": class_name})
        else:
            # TODO: Filter out useful classes.
            base_list = soup.find_all("element", {"xmi:type": "uml:Class"})

        for base in base_list:
            attrs = base.select("attribute")
            self.generate_schema(soup, base, attrs)

    def generate_schema(self, soup: BeautifulSoup, base: BeautifulSoup, attrs: ResultSet):
        """
        Converts a specific UML class to a JSON schema.

        @param soup: The base soup of the XML file to resolve references.
        @param base: The base UML class (BeautifulSoup object).
        @param attrs: A ResultSet (list of elements) containing all the individual properties.
        """

        # Create a base schema.
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema",
            "$id": f"https://github.com/open-objecten/objecttypes/{base.get('name').lower()}.json",
            "title": base.get("name"),
            # Properties are added below.
            "properties": {},
            # By default, don't allow for additional properties.
            "additionalProperties": False,
            "type": "object",
            "examples": [
                {}
            ],
        }

        properties_dict = self.filter_attributes(base.select_one("properties").attrs)
        project_dict = self.filter_attributes(base.select_one("project").attrs)

        schema.update(properties_dict)
        schema.update(project_dict)

        schema["description"] = schema.pop("documentation")
        type_convert_dictionary(schema)

        for attr in attrs:
            attr_dict = self.extract_properties(attr)

            attr_name = attr_dict.get("title")
            example = None

            if attr_dict.get("stereotype") == "enum":
                enum = soup.select_one(f'element[name="enum_{attr_name}"]')
                if enum:
                    enum_list = filter_list_duplicates([a.get("name") for a in enum.select("attribute")])
                    attr_dict["enum"] = enum_list[:]  # copy the list
                    example = enum_list[0]

            if not example:
                example = self.get_example(attr_dict.get("type"))

            schema["examples"][0][attr_name] = example
            schema["properties"][attr_name] = self.filter_attributes(attr_dict)

        # Convert the schema to JSON.
        output = json.dumps(schema, indent=2)
        with open(f"{schema['title'].lower()}.json", "w") as f:
            f.write(output)
