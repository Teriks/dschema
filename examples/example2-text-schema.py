import json
import re
import phonenumbers
import dschema


def phone_type(number):
    return phonenumbers.parse(number)


def ssn_type(ssn):
    if re.match('^\d{3}-?\d{2}-?\d{4}$', ssn):
        return ssn
    else:
        raise ValueError("'{}' is not a valid SSN.")


schema = """{
    "person": {
        "first_name": {"@required": true},
        "last_name": {"@required": true},
        "phone": {"@required": true, "@type": "phone_type"},
        "ssn": {"@required": true, "@type": "ssn_type"},
        "@required": true
    },

    "other_info": {"@dict": true, "@default": {} },

    "subscribed": {"@default": false}
}"""

# Load schema from json this time
validator = dschema.Validator(json.loads(schema))

validator.add_type('phone_type', phone_type)
validator.add_type('ssn_type', ssn_type)

data = {
    'person': {
        'first_name': 'John',
        'last_name': 'Smith',
        'phone': '+1 234 5678 9000',
        'ssn': '123-45-6789'
    },

    'other_info': {
        'website': 'www.johnsmith.com',
    }
}

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

print(result.person.first_name)  # -> John
print(result.person.last_name)  # -> Smith

print(result.person.phone)
# - > Country Code: 1 National Number: 23456789000

print(result.person.ssn)  # -> 123-45-6789

print(result.other_info)  # -> {'website': 'www.johnsmith.com'}

print(result.subscribed)  # -> False (default)
