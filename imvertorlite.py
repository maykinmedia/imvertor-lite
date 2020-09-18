import json

import click
from lxml import etree

from utils import type_conversion

NAMESPACES = {"UML": "omg.org/UML1.3"}


def convert_clazz(res, clazz):
    """
    Converts a specific UML class to a JSON schema.

    @param res: The entire `lxml` tree to resolve references.
    @param clazz: The UML class `lxml` element.
    """

    # Grab all the key-value pairs on the UML class. These contain most of the
    # information needed for defining the schema.
    tagged_values = {
        tv.get("tag"): tv.get("value")
        for tv in clazz.xpath(
            "UML:ModelElement.taggedValue/UML:TaggedValue", namespaces=NAMESPACES
        )
    }

    # Create a base schema.
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "$id": "https://objecttypes.vng.cloud/schema.json",
        "type": "object",
        "title": clazz.get("name"),
        "description": tagged_values.get("documentation", None),
        "default": {},
        # TODO: An example would be nice.
        "examples": [],
        # Properties are added below.
        "properties": {},
        # TODO: Unsure how EA indicates a required attribute.
        "required": [],
        # By default, don't allow for additional properties.
        "additionalProperties": False,
    }

    # Iterate over all attributes of the UML class and convert them to 
    # properties.
    attributes = clazz.xpath(
        "UML:Classifier.feature/UML:Attribute", namespaces=NAMESPACES
    )
    for attr in attributes:
        prop_title = attr.get("name")
        prop_name = prop_title.lower()

        # Again, key-value pairs but this time on the attribute-level. These 
        # contain the information to define the property.
        tagged_values = {
            tv.get("tag"): tv.get("value")
            for tv in attr.xpath(
                "UML:ModelElement.taggedValue/UML:TaggedValue", namespaces=NAMESPACES
            )
        }

        # Create the schema property.
        prop = {
            "$id": f"#/properties/{prop_name}",
            "type": type_conversion(tagged_values.get("type")),
            "title": f"{prop_title}",
            "description": tagged_values.get("description", ""),
            # "default": 0.0,
            "examples": [],
        }

        # Handle enumerations as a special case.
        prop_stereotype = attr.xpath(
            "UML:ModelElement.stereotype/UML:Stereotype/@name", namespaces=NAMESPACES
        )
        if len(prop_stereotype) > 0 and prop_stereotype[0] == "enum":
            enum_class_name = tagged_values.get("type")
            enum_values = res.xpath(
                f'//UML:Class[@name="{enum_class_name}"]/UML:Classifier.feature/UML:Attribute/@name',
                namespaces=NAMESPACES,
            )

            # Deduplicate items.
            enum_values = list(set(enum_values))

            # Some enumerations are empty... but are required to be filled by
            # JSON schema.
            if not enum_values:
                enum_values = ["TODO"]

            prop["enum"] = enum_values
            prop["examples"] = [enum_values[0]]

        # Add the property to the schema.
        schema["properties"][prop_name] = prop

    # Convert the schema to JSON.
    output = json.dumps(schema, indent=2)
    with open(f"{schema['title'].lower()}.json", "w") as f:
        f.write(output)


@click.command()
@click.option(
    "file_name",
    "--file",
    "-f",
    type=click.File("r"),
    required=True,
    help="An XML export from Enterprise Architect.",
)
@click.option(
    "class_name", "--name", "-n", help="The UML class name of the object to export."
)
def convert(file_name, class_name=None):
    """
    Exports one or more UML classes from an Enterprise Architect XML export to 
    JSON Schema.
    """
    res = etree.parse(file_name)

    if class_name:
        selector = f'[@name="{class_name}"]'
    else:
        # TODO: Filter out usefull classes.
        selector = ""

    clazzes = res.xpath(f"//UML:Class{selector}", namespaces=NAMESPACES)

    for clazz in clazzes:
        convert_clazz(res, clazz)


if __name__ == "__main__":
    convert()
