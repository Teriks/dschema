import dschema

# specifying defaults in a nested property
# will completely fill the property tree
# if it does not exist in your data

schema = {
    'a': {
        'b': {
            'c': dschema.prop(default='d')
        }
    }
}

r = dschema.Validator(schema).validate({}, namespace=True)

print(r.a.b.c)  # -> prints: d

# you can define a default value for nodes with
# nested properties, the default value must match
# the schema of the node it is defined in

schema = {
    'a': {
        dschema.Default: {'b': {'c': 1}},
        'b': {
            'c': dschema.prop(type=int)
        }
    }
}

r = dschema.Validator(schema).validate({}, namespace=True)

print(r.a.b.c)  # -> prints: 1

# this is an error because the default value
# does not match the schema

schema = {
    'a': {
        dschema.Default: {'b': {'c': 'notint'}},
        'b': {
            'c': dschema.prop(type=int)
        }
    }
}

try:
    # exception here..
    dschema.Validator(schema).validate({'a': None})
except dschema.SchemaDefaultError as e:
    print(e)

# you validator functions return values are
# always considered when processing default values

schema = {
    'a': {
        dschema.Default: {'b': {'c': 1}},
        'b': {
            'c': dschema.prop(type=lambda x: x + 1)
        }
    }
}

r = dschema.Validator(schema).validate({}, namespace=True)

# ===

print(r.a.b.c)  # prints: 2

schema = {
    'a': dschema.prop(default=1, type=lambda x: x + 1)
}

r = dschema.Validator(schema).validate({'a': None}, namespace=True)

print(r.a)  # prints: 2
