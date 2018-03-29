# Copyright (c) 2018, Teriks
# All rights reserved.
#
# dschema is distributed under the following BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from copy import deepcopy

__all__ = ['Namespace',
           'ValidationError',
           'TypeValidationError',
           'SchemaError',
           'Default',
           'Required',
           'Dict',
           'Type',
           'prop',
           'Validator']


class Namespace:
    """Simple dynamic object, optimized for dschema."""

    def __init__(self, dictionary):
        self.__dict__ = dictionary

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Namespace({})'.format(", ".join("{}={}".format(k, repr(v)) for k, v in self.__dict__.items()))


class ValidationError(Exception):
    """Thrown on any validation error, such as missing required properties."""

    def __init__(self, message):
        super().__init__(message)


class TypeValidationError(ValidationError):
    """Thrown when a type validation function throws on an incoming value."""

    def __init__(self, message, type_exception=None):
        super().__init__(message)
        self.type_exception = type_exception


class SchemaError(Exception):
    """Thrown for errors related to the schema definition itself."""

    def __init__(self, message):
        super().__init__(message)


#: Used to define a default value for a schema property
Default = '@default'

#: Used to indicate a given schema node/property is required
Required = '@required'

#: Used to indicate a schema property should allow a raw dictionary to pass through as a value
Dict = '@dict'

#: Used to define a custom validation function for a schema node/property
Type = '@type'


def prop(**kwargs):
    r"""Helper that returns a schema property specification from keyword arguments.

    :param \**kwargs:
        See below

    :Keyword Arguments:
        * *default* (``object``) --
          Default value when none is present in the validated dictionary.
        * *required* (``object``) --
          Is this key/value pair required to be present?
        * *type* (``callable``) --
          The validation callable to use on the incoming value.
        * *dict* (``bool``) --
          Should the value be interpreted as a raw nested dictionary?
    """
    r = dict()
    for k, v in kwargs.items():
        r['@' + k] = v
    return r


class Validator:
    """Schema validator class"""

    def __init__(self, schema):
        """
        :param schema: Your schema definition
        """

        #: schema dictionary (reassignable).
        self.schema = schema

        self.types = dict()
        """Types dictionary, should contain type validator callables by name (reassignable).
        
           Must implement ``get(key, default)`` and ``types['key']`` like a python :py:class:`dict`."""

    def add_type(self, name, validation_function):
        """Register a type validation callable that can be referenced by name in the schema.
        
        See: :py:attr:`~dschema.Validator.types`

        :param name: Name which can be referenced in the schema using a string.
        :param validation_function: Associated validation function.
        """
        self.types[name] = validation_function

    def remove_type(self, name):
        """Remove an existing type validation callable.

        See: :py:func:`~dschema.Validator.add_type` and :py:attr:`~dschema.Validator.types`

        :param name: The name previously registered with :py:func:`~dschema.Validator.add_type`
        """
        del self.types[name] # pragma: no cover

    @staticmethod
    def _fill_schema_defaults(node, return_namespace):
        node = deepcopy(node)

        if Default in node:
            default = node[Default]
            if return_namespace and Dict not in node and isinstance(default, dict):
                return Namespace(default)
            else:
                return default

        stack = [node]
        while stack:
            nd = stack.pop()
            for k, v in nd.items():
                if isinstance(v, dict):
                    if Default in v:
                        default = v[Default]
                        if return_namespace and Dict not in v and isinstance(default, dict):
                            nd[k] = Namespace(default)
                        else:
                            nd[k] = default
                    else:
                        stack.append(v)

                        if return_namespace:
                            if Dict in v:
                                del v[Dict]
                            else:
                                nd[k] = Namespace(v)
                        elif Dict in v:
                            del v[Dict]

        if return_namespace and Dict not in node and isinstance(node, dict):
            return Namespace(node)
        else:
            return node

    def _check_schema(self, dictionary, schema, namespace, return_namespace, allow_extra_keys):

        stack = [(dictionary, schema, namespace)]

        while stack:
            dict_node, schema_node, namespace = stack.pop()

            dict_node_is_dict = isinstance(dict_node, dict)

            for schema_key, schema_value in schema_node.items():
                schema_value_is_dict = isinstance(schema_value, dict)

                if not dict_node_is_dict or not (schema_key in dict_node):
                    if schema_value_is_dict and schema_value.get(Required, False):
                        namespace = "{}.{}".format(namespace, schema_key) if namespace else schema_key

                        raise ValidationError("'{}' is required but missing.".format(namespace))

                    if dict_node_is_dict and schema_value_is_dict:
                        dict_node[schema_key] = self._fill_schema_defaults(schema_value, return_namespace)

                    continue

                node_value = dict_node.get(schema_key, None)

                if not schema_value_is_dict:
                    default = None
                    is_dict = schema_value == Dict
                    the_type = None if is_dict else schema_value
                else:
                    if Default in schema_value:
                        if Required in schema_value:
                            raise SchemaError("Schema node '{}' cannot be required and also have a default value."
                                              .format(schema_key))
                        else:
                            default = schema_value[Default]
                    else:
                        default = None

                    is_dict = schema_value.get(Dict, False)
                    the_type = schema_value.get(Type, None)

                next_namespace = "{}.{}".format(namespace, schema_key) if namespace else schema_key

                if node_value is None and default:
                    dict_node[schema_key] = default
                else:
                    if isinstance(the_type, str):
                        found_type = self.types.get(the_type, None)

                        if found_type:
                            the_type = found_type
                        else:
                            raise SchemaError("'{}' schema type callable '{}' not provided."
                                              .format(next_namespace, the_type))

                    if the_type:
                        try:
                            dict_node[schema_key] = the_type(node_value)
                        except Exception as e:
                            raise TypeValidationError("'{}' failed type validation: {}"
                                                      .format(next_namespace, str(e)), e)

                if is_dict:
                    continue

                next_schema_node = schema_node[schema_key]
                if isinstance(next_schema_node, dict):
                    stack.append((dict_node[schema_key], next_schema_node, next_namespace))

                if return_namespace and Dict not in schema_value and isinstance(node_value, dict):
                    dict_node[schema_key] = Namespace(node_value)

            if not allow_extra_keys and isinstance(dict_node, dict):
                key_diff = dict_node.keys() - schema_node.keys()
                if len(key_diff):
                    raise ValidationError(
                        "Namespace '{}' contains extraneous keys: {}.".format(namespace if namespace else '.',
                                                                              key_diff))

            elif return_namespace and isinstance(dict_node, dict):
                for key in dict_node.keys() - schema_node.keys():
                    dict_node[key] = self._namespace_dicts(dict_node[key])

        return dictionary

    def validate(self, dictionary, copy=True, namespace=False, extra_keys=False):
        """Validate a dictionary object using the defined schema and return it a copy.

        Defaults defined in the schema will be filled out if they do not exist in the incoming data.

        :param copy: Whether or not to deep copy the input dictionary before processing, if this is not
                     done, then the input dictionary will be modified to a useless state. validate can
                     run faster if do not plan to use the input dictionary again and you use **copy=False**.

        :param dictionary: (``dict``) object to validate.
        :param namespace: If ``True``, return a deserialized :py:class:`dschema.Namespace` object.
        :param extra_keys: Allow extra key value pairs that do not exist in the schema to pass through without
                                 exception. In effect, only run validation on keys which are found to exist in the
                                 schema, and let others always pass through if they have no schema defined for them.

        :return: Processed input dictionary
        """

        result = self._check_schema(deepcopy(dictionary) if copy else dictionary,
                                    self.schema, '', namespace, extra_keys)

        if namespace:
            return Namespace(result)
        else:
            return result

    @staticmethod
    def _namespace_dicts(dictionary):
        if not isinstance(dictionary, dict):
            return dictionary

        stack = [dictionary]
        while stack:
            d = stack.pop()
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, dict):
                        stack.append(v)
                        d[k] = Namespace(v)

        return Namespace(dictionary)
