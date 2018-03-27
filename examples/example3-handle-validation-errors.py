import dschema

validator = dschema.Validator({
    'app_auth': {
        'id': dschema.prop(required=True),
        'token': dschema.prop(required=True),

        dschema.Required: True
        # You must specify a namespace as required
        # if you want it to be required, even if it
        # contains required properties
    },

    'integer': dschema.prop(required=True, type=int)
})


# Handling of missing required values
# ===================================

data = {
    'app_auth': {
        'token': 'somerandomthing',
    },
    'integer': 1
}

try:
    validator.validate(data)
except dschema.ValidationError as e:
    # message about 'app_auth.id' being required but missing...
    print(e)

data = {'integer': 1}

try:
    validator.validate(data)
except dschema.ValidationError as e:
    # message about 'app_auth' being required but missing...
    print(e)


# Handling type validation errors
# ===============================

data = {
    'app_auth': {
        'id': 12345,
        'token': 'somerandomthing'
    },
    'integer': 'notinteger'
}

try:
    validator.validate(data)
except dschema.ValidationError as e:
    # message about 'integer' failing type validation...
    print(e)

try:
    validator.validate(data)
except dschema.TypeValidationError as e:
    # be more specific and cache the TypeValidationError

    # message about 'integer' failing type validation...
    print(e)

    # print the exception that came out of the validator function
    print(e.type_exception)


# Handling of extraneous key values
# =================================

data = {
    'app_auth': {
        'id': 12345,
        'token': 'somerandomthing',
        'extra_stuff': 'should not be here'
    },
    'integer': 1
}


try:
    validator.validate(data)
except dschema.ValidationError as e:
    # Message about:
    # namespace 'app_auth' containing extraneous keys {'extra_stuff'}
    print(e)


# Allow extra keys to pass through into the result...
result = validator.validate(data, extra_keys=True)

print(result['app_auth']['extra_stuff'])  # -> prints: should not be here

