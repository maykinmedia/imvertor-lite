import sys

import click

from parsers import EnterpriseArchitect, AmsterdamSchema

PARSERS = {
    "enterprise_architect": EnterpriseArchitect,
    "amsterdam_schema": AmsterdamSchema,
}


@click.command()
@click.option(
    "file_name",
    "--file",
    "-f",
    required=True,
    help="Specify the name of the input file.",
)
@click.option(
    "class_name", "--name", "-n", help="The UML class name of the object to export."
)
@click.option(
    "encoding", "--encoding", "-e", help="Specify the encoding of the XML file (optional).",
)
@click.option(
    "parser", "--parser", "-p", help=f"Supported parsers: {', '.join(PARSERS)}.",
)
def convert(file_name, class_name=None, encoding=None, parser=None):
    """
    Exports one or more UML classes from an Enterprise Architect XML export to 
    JSON Schema.
    """

    if parser in PARSERS:
        parser = PARSERS[parser]
    elif file_name.endswith(".json"):
        parser = PARSERS['amsterdam_schema']
    elif file_name.endswith(".xml"):
        parser = PARSERS['enterprise_architect']
    else:
        print("Unsupported format.")
        sys.exit(1)

    parser().process(file_name=file_name, class_name=class_name, encoding=encoding)
    sys.exit(0)


if __name__ == "__main__":
    convert()
