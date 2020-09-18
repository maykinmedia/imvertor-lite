=============
Imvertor Lite
=============

:Version: 0.1.0
:Source: https://github.com/maykinmedia/imvertor-lite
:Keywords: gegevensmodel, json-schema, eap
:PythonVersion: 3.7

Convert an UML class to a JSON schema.

Developed by `Maykin Media B.V.`_.


Introduction
============

Create a JSON schema based on an `Enterprise Architect`_ UML class. Typically 
used for converting a class in the `Gemeentelijk Gegevensmodel`_ created by the
municipality of Delft.

The name "Imvertor Lite" refers to the `Imvertor`_ project as a joke since it 
was initially considered to be a really bad idea while now creating a similar
tool. This tool is in no way affiliated with Imvertor.

Installation
============

.. code:: bash

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements

Usage
=====

1. Get an XML export of an Enterprise Architect file. For example, as provided 
   by the municipality of Delft in their Gemeentelijk Gegevensmodel:

   .. code:: bash

       $ wget -O ggm_original.xml https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel/raw/master/gemeentelijk%20gegevensmodel.xml
       $ iconv -f utf-8 -t ascii -c ggm_original.xml -o ggm.xml

2. Run the converter on the downloaded XML file and target a specific class by 
   its name:

   .. code:: bash

       $ python imvertorlite -f ggm.xml -n Boom

3. The result is in a file named after the class name, in this case 
   ``boom.json``.


.. _`Enterprise Architect`: https://www.sparxsystems.eu/enterprise-architect/
.. _`Gemeentelijk Gegevensmodel`: https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel
.. _`JSON schema`: https://json-schema.org/
.. _`Imvertor`: https://github.com/Imvertor

Licence
=======

Copyright © Maykin Media B.V., 2020

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
