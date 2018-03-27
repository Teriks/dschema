import dschema

# These are the only two cases currently in which this
# exception is raised.

# One is when you specify a required property as having
# a default value.

schema = {
    'bad': dschema.prop(required=True, default='cant-have-both')
}

try:
    dschema.Validator(schema).validate({'bad': 'stuff'})
except dschema.SchemaError as e:

    # Message about 'required' and 'default' being mutually exclusive
    print(e)


# The other is when you don't provide a validation handler
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

except dschema.SchemaError as e:

    # Message about:
    # 'no_type_validator' schema type callable 'int' not provided.
    print(e)
