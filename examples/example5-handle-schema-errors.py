import dschema


# specifying a required property as
# having a default value.

schema = {
    'bad': dschema.prop(required=True, default='cant-have-both')
}

try:
    dschema.Validator(schema).validate({'bad': 'stuff'})
except dschema.SchemaError as e:

    # Message about 'required' and 'default' being mutually exclusive
    print(e)


# Not providing a validation handler
# for a type specified as a string

schema = {
    'no_type_validator': dschema.prop(required=True, type='int')
}

try:
    validator = dschema.Validator(schema)

    # Validator.add_type must be used to add
    # something that handles 'int' ...

    # validator.add_type('int', int)

    validator.validate({'no_type_validator': 1})

except dschema.SchemaMissingTypeError as e:

    # Message about:
    # 'no_type_validator' schema type callable 'int' not provided.
    print(e)

# providing a default value that does
# not validate against the schema

schema = {
    'node':
        {
            dschema.Default: {'bad': {'prop': 'notint'}},
            'bad': {
                'prop': dschema.prop(type=int)
             }
        }
}

try:
    validator = dschema.Validator(schema)

    validator.validate({})

except dschema.SchemaDefaultError as e:

    # Message about:
    # 'bad.prop' failed type validation: invalid literal for
    # int() with base 10: 'notint'
    print(e)
