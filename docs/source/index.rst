Welcome to dschema's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: API Documentation
   
   dschema

About
=====

dschema is a small library for validating the content of python dictionary objects against a schema.

The schema can be defined in code or entirely as text (parsed from JSON generally)

dschema was made for validating config files written in JSON, and allows for specifying
required and default property values, and also custom type validation.


Usage
=====

.. toctree::
   :maxdepth: 2

   defining_schema_with_code
   defining_schema_with_text
   defining_default_values
   handling_validation_errors
   handling_schema_definition_errors



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
