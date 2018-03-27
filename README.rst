About dschema
=============

.. |codecov| image:: https://codecov.io/gh/Teriks/dschema/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Teriks/dschema

.. |Master Documentation Status| image:: https://readthedocs.org/projects/dschema/badge/?version=latest
   :target: http://dschema.readthedocs.io/en/latest/?badge=latest

|Master Documentation Status| |codecov|

dschema is a small library for validating the content of python dictionary objects against a schema.

The schema can be defined in code or entirely as text (parsed from json generally)

dschema was mainly made for validating config files written in JSON.


Example
=======

See documentation link for more examples

.. code-block:: python

    import re
    import phonenumbers
    import dschema


    # https://github.com/daviddrysdale/python-phonenumbers
    # pip install phonenumbers


    def phone_type(number):
        # Exceptions are validation errors
        # Very similar design to the "argparse" module
        return phonenumbers.parse(number)


    def ssn_type(ssn):
        if re.match('^\d{3}-?\d{2}-?\d{4}$', ssn):
            return ssn
        else:
            raise ValueError('"{}" is not a valid SSN.')


    schema = {
        'person': {
            'first_name': dschema.prop(required=True),
            'last_name': dschema.prop(required=True),
            'phone': dschema.prop(required=True, type=phone_type),
            'ssn': dschema.prop(required=True, type='ssn_type'),

            dschema.Required: True
            # "person" namespace is required, you must specify
            # even if "person" itself contains required properties
        },

        # Allow a raw dictionary value to pass through

        'other_info': dschema.prop(default=dict(), dict=True),

        # default to False if not present

        'subscribed': dschema.prop(default=False, type=bool)
    }

    validator = dschema.Validator(schema)

    # you can use this to add types that are recognized by name.
    # which is useful if you want your schema to be entirely textual

    validator.add_type('ssn_type', ssn_type)

    # you will need to define default types on your own
    # if you want to reference them by name

    # validator.add_type('int', int)


    data = {
        'person': {
            'first_name': "John",
            'last_name': "Smith",
            'phone': '+1 234 5678 9000',
            'ssn': '123-45-6789'
        },

        'other_info': {
            'website': 'www.johnsmith.com',
        }
    }

    # If namespace is left False, a plain dictionary is returned

    result = validator.validate(data, namespace=True)

    print(result)

    # Prints: (un-indented)

    # Namespace(
    #     person=Namespace(
    #         first_name='John',
    #         last_name='Smith',
    #         phone=PhoneNumber(...),
    #         ssn='123-45-6789'),
    #     other_info={'website': 'www.johnsmith.com'},
    #     subscribed=False
    # )


    # Each Namespace is just a dynamic object

    print(result.person.first_name)  # -> John
    print(result.person.last_name)  # -> Smith

    print(result.person.phone)
    # - > Country Code: 1 National Number: 23456789000

    print(result.person.ssn)  # -> 123-45-6789

    print(result.other_info)  # -> {'website': 'www.johnsmith.com'}

    print(result.subscribed)  # -> False (default)
