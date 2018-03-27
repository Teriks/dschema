Welcome to dschema's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:
   
   dschema

About
=====

dschema is a small library for validating the content of python dictionary objects against a schema.

The schema can be defined in code or entirely as text (parsed from JSON generally)

dschema was made for validating config files written in JSON, and allows for specifying
required and default property values, and also custom type validation.


Examples
========

Defining schema with code
-------------------------

.. literalinclude:: ../../examples/example1-basic.py
 :language: python


Defining schema with text
-------------------------

.. literalinclude:: ../../examples/example2-text-schema.py
 :language: python


Handling validation errors
--------------------------

.. literalinclude:: ../../examples/example3-handle-validation-errors.py
 :language: python


Handling schema definition errors
---------------------------------

.. literalinclude:: ../../examples/example4-handle-schema-errors.py
 :language: python


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
