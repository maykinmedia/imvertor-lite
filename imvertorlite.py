import json
import sys
import click
from bs4 import BeautifulSoup, ResultSet, Tag
from utils import type_conversion, type_convert_dictionary
import cchardet


def get_initial_value(element: Tag):
    initial = element.select_one("initial").get("body")
    if initial:
        return initial
    else:
        return None


def extract_properties(attr: Tag):
    attr_name = attr.get("name")
    attr_dict = {
        "$id": f"#/properties/{attr_name}",
        "title": f"{attr_name}",
    }

    attr_props = attr.select_one("properties")
    attr_dict.update(
        type_convert_dictionary(attr_props.attrs))

    initial_value = get_initial_value(attr)
    if initial_value:
        attr_dict["default"] = type_conversion(initial_value)

    attr_type = attr_props.get("type")
    if attr_type:
        attr_dict["type"] = type_conversion(attr_type)

    stereotype = attr.select_one("stereotype")
    if stereotype:
        attr_dict["stereotype"] = stereotype.get("stereotype")

    documentation = attr.select_one("documentation")
    if documentation:
        attr_dict["description"] = documentation.get("value")

    tags = attr.select_one("tags").select("tag")
    if tags:
        attr_dict["tags"] = [{"name": tag.get("name"),
                              "value": tag.get("value"),
                              "notes": tag.get("notes")} for tag in tags]

    return attr_dict


def generate_schema(soup: BeautifulSoup, base: BeautifulSoup, attrs: ResultSet):
    """
    Converts a specific UML class to a JSON schema.

    @param soup: The base soup of the XML file to resolve references.
    @param base: The base UML class (BeautifulSoup object).
    @param attrs: A ResultSet (list of elements) containing all the individual properties.
    """

    # Create a base schema.
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "$id": "https://objecttypes.vng.cloud/schema.json",
        "title": base.get("name"),
        # Properties are added below.
        "properties": {},
        # By default, don't allow for additional properties.
        "additionalProperties": False,
        "type": "object",
    }
    schema.update(
        type_convert_dictionary(base.select_one("properties").attrs)
    )
    schema.update(
        type_convert_dictionary(base.select_one("project").attrs)
    )

    schema['description'] = schema.pop('documentation')

    for attr in attrs:
        attr_dict = extract_properties(attr)

        attr_name = attr_dict.get("title")
        schema["properties"][attr_name] = attr_dict

        if attr_dict.get("stereotype") == "enum":
            enum = soup.select_one(f'element[name="enum_{attr_name}"]')
            if enum:
                enum_list = list(set([a.get('name') for a in enum.select("attribute")]))
                schema["properties"][attr_name]["examples"] = [enum_list[0]]
                schema["properties"][attr_name]["enum"] = enum_list[:]  # copy the list

                # Convert the schema to JSON.
                output = json.dumps(schema, indent=2)
                with open(f"{schema['title'].lower()}.json", "w") as f:
                    f.write(output)


def process_enterprise_architect(file_name, class_name, encoding):
    """
    Process the enteprise architect format (XML)

    @param soup: The base soup of the XML file to resolve references.
    @param base: The base UML class (BeautifulSoup object).
    @param attrs: A ResultSet (list of elements) containing all the individual properties.
    """

    with open(file_name, "r", encoding=encoding if encoding else "latin-1") as f:
        data = f.read()

    soup = BeautifulSoup(data, "lxml")

    if class_name:
        base_list = soup.find_all('element', {'xmi:type': 'uml:Class', 'name': class_name})
    else:
        # TODO: Filter out useful classes.
        base_list = soup.find_all('element', {'xmi:type': 'uml:Class'})

    for base in base_list:
        attrs = base.select("attribute")
        generate_schema(soup, base, attrs)


def process_amsterdam_schema(file_name, encoding='utf-8'):
    """
    Process the Amsterdam Schema format (JSON)

    @param file_name: The name of the JSON file.
    @param encoding: The encoding of the given JSON file (Default: "utf-8").
    """

    with open(file_name, "r", encoding=encoding) as f:
        obj = json.load(f)

    schemas = obj['tables']
    for schema in schemas:
        schema['properties'] = schema.pop('schema')
        schema['type'] = 'object'

        for key in list(schema['properties'].keys()):
            if key not in ['properties']:
                schema[key] = schema['properties'].pop(key)

        properties = schema['properties'].pop('properties')
        for key, dic in properties.items():
            if key not in ['schema']:
                dic['$id'] = f'#/properties/{key}'
                dic['title'] = key
                schema['properties'][key] = dic

        schema['required'].remove('schema')  # Remove 'schema' property

        with open(f"{schema['title'].lower()}.json", "w") as f:
            json.dump(schema, f, indent=2)


@click.command()
@click.option(
    "file_name",
    "--file",
    "-f",
    required=True,
    help="Supported formats: Enterprise Architect XML, Amsterdam Schema JSON.",
)
@click.option(
    "class_name", "--name", "-n", help="The UML class name of the object to export."
)
@click.option(
    "encoding", "--encoding", "-e", help="Specify the encoding of the XML file (optional).",
)
def convert(file_name, class_name=None, encoding=None):
    """
    Exports one or more UML classes from an Enterprise Architect XML export to 
    JSON Schema.
    """

    if file_name.endswith('.json'):
        process_amsterdam_schema(file_name, encoding)
    elif file_name.endswith('.xml'):
        process_enterprise_architect(file_name, class_name, encoding)
    else:
        print('Unsupported format.')
        sys.exit(1)


if __name__ == "__main__":
    convert()
