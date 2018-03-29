import os
import sys
import unittest

import dschema

script_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(1, os.path.abspath(
    os.path.join(script_dir, os.path.join('..', '..'))))


class ValidatorTest(unittest.TestCase):

    def test_default_values(self):
        validator = dschema.Validator({
            'a': {
                'b': {
                    'c': dschema.prop(default='d')
                },
            },
            'e': {
                'f': {
                    '@default': 'g'
                }
            },
            'h': {'@default': 'i'},

            'j': dschema.prop(default={'test': 1}, dict=True),

            'l': {
                'm': dschema.prop(default={'test2': 2}, dict=True)
            },
            'o': {
                'p': {
                    'q': dschema.prop(default={'test3': 3})
                },
            },
            'r': {
                's': {
                    dschema.Default: {'t': 'u'}, dschema.Dict: True,
                    't': 'a'
                }
            }
        })

        result = validator.validate({}, namespace=True)

        self.assertTrue(hasattr(result, 'a'))

        self.assertTrue(hasattr(result.a, 'b'))

        self.assertTrue(hasattr(result.a.b, 'c'))

        self.assertEqual(result.a.b.c, 'd')

        self.assertTrue(hasattr(result, 'e'))

        self.assertTrue(hasattr(result.e, 'f'))

        self.assertEqual(result.e.f, 'g')

        self.assertEqual('i', result.h)

        self.assertTrue(hasattr(result, 'h'))

        self.assertTrue(hasattr(result, 'j'))

        self.assertTrue(hasattr(result, 'l'))

        self.assertTrue(hasattr(result.l, 'm'))

        self.assertDictEqual({'test': 1}, result.j)

        self.assertDictEqual({'test2': 2}, result.l.m)

        self.assertTrue(hasattr(result, 'o'))

        self.assertTrue(hasattr(result.o, 'p'))

        self.assertTrue(hasattr(result.o.p, 'q'))

        self.assertTrue(hasattr(result.o.p.q, 'test3'))

        self.assertEqual(result.o.p.q.test3, 3)

        self.assertTrue(hasattr(result, 'r'))

        self.assertTrue(hasattr(result.r, 's'))

        self.assertDictEqual(result.r.s, {'t': 'u'})

        result = validator.validate({'r': {'s': {'t': 'a'}}}, namespace=True)

        self.assertTrue(hasattr(result, 'r'))

        self.assertTrue(hasattr(result.r, 's'))

        self.assertDictEqual(result.r.s, {'t': 'a'})

        #

        result = validator.validate({'h': None})

        self.assertIn('a', result)

        self.assertIn('b', result['a'])

        self.assertIn('c', result['a']['b'])

        self.assertEqual('d', result['a']['b']['c'])

        self.assertIn('e', result)

        self.assertIn('f', result['e'])

        self.assertEqual('g', result['e']['f'])

        self.assertEqual('i', result['h'])

        self.assertDictEqual({'test': 1}, result['j'])

        self.assertDictEqual({'test2': 2}, result['l']['m'])

        self.assertIn('r', result)

        self.assertIn('s', result['r'])

        self.assertIn('t', result['r']['s'])

        self.assertDictEqual(result['r']['s'], {'t': 'u'})

        result = validator.validate({'r': {'s': {'t': 'a'}}})

        self.assertIn('r', result)

        self.assertIn('s', result['r'])

        self.assertIn('t', result['r']['s'])

        self.assertDictEqual(result['r']['s'], {'t': 'a'})

    def test_namespace_dicts_algorithm(self):
        v = dschema.Validator({})

        ns = v._namespace_dicts({'a': {'b': {'c': 1, 'd': 2}}})

        self.assertTrue(hasattr(ns, 'a'))
        self.assertTrue(hasattr(ns.a, 'b'))

        self.assertEqual(type(ns.a.b), dschema.Namespace)
        self.assertEqual(ns.a.b.c, 1)
        self.assertEqual(ns.a.b.d, 2)

    def test_application_of_schema_to_defaults(self):
        v = dschema.Validator(schema={
            "node":
                {
                    dschema.Default: {"node2": {"a": 1}},
                    "node2":
                        {
                            "a": dschema.prop(required=True, type=lambda x: x + 1)
                        }
                }
        })

        r = v.validate({"node": None}, namespace=True)

        self.assertEqual(r.node.node2.a, 2)

        v.schema = {
            "node":
                {
                    dschema.Default: {"a": 1},
                    "a": dschema.prop(required=True, type=lambda x: x + 1)
                }
        }

        r = v.validate({}, namespace=True)

        self.assertEqual(r.node.a, 2)

        v.schema = {
            "node":
                {
                    dschema.Default: {"node2": {"a": 1}},
                    "node2":
                        {
                            "a": dschema.prop(required=True, type=lambda x: x + 1)
                        }
                }
        }

        r = v.validate({})

        self.assertEqual(r['node']['node2']['a'], 2)

        v.schema = {
            "node":
                {
                    dschema.Default: {"a": 1},
                    "a": dschema.prop(required=True, type=lambda x: x + 1)
                }
        }

        r = v.validate({"node": None})

        self.assertEqual(r['node']['a'], 2)

        v.schema = {
            "a": dschema.prop(default='notint', type=int)
        }

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({})

        self.assertTrue(isinstance(err.exception.validation_error, dschema.TypeValidationError))

        v.schema = {
            "a": {
                dschema.Default: {"b": None},
                "b": {
                    dschema.Default: None,
                    "c": dschema.prop(required=True, type=int)
                }
            }
        }

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({})

        self.assertTrue(isinstance(err.exception.validation_error, dschema.MissingKeyError))

        v.schema = {
            'a': {
                'b': {
                    'c': dschema.prop(default='d', type=lambda x: x + 'd')
                },
            }}

        r = v.validate({}, namespace=True)

        self.assertEqual(r.a.b.c, 'dd')

        v.schema = {
            'a': {
                'b': {
                    'c': dschema.prop(default='d', type=lambda x: x + 'd')
                },
            }}

        r = v.validate({})

        self.assertEqual(r['a']['b']['c'], 'dd')

        v.schema = {
            'a': {
                'b': {
                    'c': dschema.prop(default='notint', type=int)
                },
            }}

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({}, namespace=True)

        self.assertTrue(isinstance(err.exception.validation_error, dschema.TypeValidationError))

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({})

        self.assertTrue(isinstance(err.exception.validation_error, dschema.TypeValidationError))

        v.schema = {
            'a': {
                'b': {
                    'c': {
                        dschema.Default: {'d': 4},
                        "d": dschema.prop(default=3)
                    }
                },
            }
        }

        r = v.validate({}, namespace=True)

        self.assertTrue(r.a.b.c.d, 4)

        v.schema = {
            'a': {
                'b': {
                    'c': {
                        dschema.Default: {'d': 4},
                        "d": dschema.prop(default=3)
                    }
                },
            }
        }

        r = v.validate({})

        self.assertTrue(r['a']['b']['c']['d'], 4)

        v.schema = {
            'a': {
                'b': {
                    'c': {
                        dschema.Default: {'d': 'notint'},
                        "d": dschema.prop(type=int)
                    }
                },
            }
        }

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({}, namespace=True)

        self.assertTrue(isinstance(err.exception.validation_error, dschema.TypeValidationError))

        with self.assertRaises(dschema.SchemaDefaultError) as err:
            v.validate({})

        self.assertTrue(isinstance(err.exception.validation_error, dschema.TypeValidationError))

    def test_fill_defaults_algorithm(self):
        # test the defaults filler algorithm

        v = dschema.Validator({})

        schema = {
            'l': {
                '@dict': True,
                'm': dschema.prop(default={'test1': 1}, dict=True)
            },
            'a': {
                'b': dschema.prop(default={'test2': 2}, dict=True)
            }
        }

        r = v._fill_schema_defaults(schema, '.', True)

        self.assertTrue(hasattr(r, 'l'))

        self.assertDictEqual(r.l, {'m': {'test1': 1}})

        self.assertTrue(hasattr(r, 'a'))
        self.assertTrue(hasattr(r.a, 'b'))

        self.assertDictEqual(r.a.b, {'test2': 2})

        r = v._fill_schema_defaults(schema, '.', False)

        self.assertDictEqual(r, {'l': {'m': {'test1': 1}}, 'a': {'b': {'test2': 2}}})

        r = v._fill_schema_defaults({dschema.Default: 1}, '.', False)

        self.assertEqual(r, 1)

        r = v._fill_schema_defaults({dschema.Default: {'test': 1}}, '.', True)

        self.assertEqual(type(r), dschema.Namespace)
        self.assertTrue(hasattr(r, 'test'))
        self.assertEqual(r.test, 1)

        r = v._fill_schema_defaults({dschema.Dict: True, dschema.Default: {'test': 1}}, '.', True)

        self.assertEqual(type(r), dict)
        self.assertIn('test', r)
        self.assertEqual(r['test'], 1)

        r = v._fill_schema_defaults({dschema.Dict: True, dschema.Default: {'test': 1}}, '.', False)

        self.assertEqual(type(r), dict)
        self.assertIn('test', r)
        self.assertEqual(r['test'], 1)

    def test_validation_errors(self):
        validator = dschema.Validator({
            'app_auth': {
                'id': dschema.prop(required=True),
                'token': dschema.prop(required=True),
                dschema.Required: True
            },

            'integer': dschema.prop(required=True, type=int)
        })

        data = {
            'app_auth': {
                'token': 'somerandomthing'
            },
            'integer': 1
        }

        with self.assertRaises(dschema.MissingKeyError):
            validator.validate(data)

        data = {'integer': 1}

        with self.assertRaises(dschema.MissingKeyError):
            validator.validate(data)

        data = {
            'app_auth': {
                'id': 12345,
                'token': 'somerandomthing'
            },
            'integer': 'notinteger'
        }

        with self.assertRaises(dschema.TypeValidationError):
            validator.validate(data)

    def test_schema_errors(self):
        schema = {
            'bad': dschema.prop(required=True, default='cant-have-both')
        }

        with self.assertRaises(dschema.SchemaError):
            dschema.Validator(schema).validate({'bad': 'stuff'})

        schema = {
            'no_type_validator': dschema.prop(required=True, type='int')
        }

        with self.assertRaises(dschema.SchemaMissingTypeError):
            dschema.Validator(schema).validate({'no_type_validator': 1})

    def test_dict(self):
        validator = dschema.Validator({
            'dict': dschema.Dict,
            'in_schema_not_dict': dschema.prop(default=dict())
        })

        # shouldn't throw
        result = validator.validate({
            'dict': {'a': 'b'},
            'not_dict': {'c': 'd'},  # unhandled values should be namespacified when return_namespace=True,
            'in_schema_not_dict': {'e': 'f'}
        }, namespace=True, extra_keys=True)

        self.assertDictEqual(result.dict, {'a': 'b'})

        self.assertTrue(isinstance(result.not_dict, dschema.Namespace))

        self.assertEqual(result.not_dict.c, 'd')

        self.assertTrue(isinstance(result.in_schema_not_dict, dschema.Namespace))

        self.assertTrue(result.in_schema_not_dict.e, 'f')

    def test_extraneous_values(self):
        validator = dschema.Validator({
            'namespace': {
                'nested': {
                    'a': dschema.prop(required=True),
                    dschema.Required: True
                },
                dschema.Required: True
            }
        })

        with self.assertRaises(dschema.ExtraKeysError):
            validator.validate({
                'namespace': {
                    'nested': {
                        'a': 1,
                        'b': 2  # not allowed
                    }
                }
            })

        with self.assertRaises(dschema.ExtraKeysError):
            validator.validate({
                'namespace': {
                    'nested': {
                        'a': 1
                    },
                    'b': 2  # not allowed
                }
            })

        with self.assertRaises(dschema.ExtraKeysError):
            validator.validate({
                'namespace': {
                    'nested': {
                        'a': 1
                    }
                },
                'b': 2  # not allowed
            })

    def test_required(self):
        validator = dschema.Validator({
            'test1':
                {
                    'a': dschema.prop(required=True)
                },
            'test2':
                {
                    'test3': {
                        dschema.Required: True,
                        'a': dschema.prop(default=1),
                        'b': dschema.prop(default=2)
                    }
                },
            'test4':
                {
                    'test5': {
                        dschema.Required: True,
                        'a': dschema.prop(required=True),
                        'b': dschema.prop(default=2)
                    }
                }
        })

        # test2 is optional, test3 must exist if test2 exist though
        # shouldn't throw
        validator.validate({
            'test1': {
                'a': 1
            },
        })

        with self.assertRaises(dschema.ValidationError):
            # test.a must exist
            validator.validate({
                'test1': 1,
            })

        with self.assertRaises(dschema.ValidationError):
            # test2.test3 must exist
            validator.validate({
                'test1': {
                    'a': 1
                },
                'test2': 1
            })

        # test2 is optional, test3 must exist if test2 exist though
        # shouldn't throw
        validator.validate({
            'test1': {
                'a': 1
            },
            'test2': {
                'test3': {
                    'a': 1
                }
            }
        })

        with self.assertRaises(dschema.ValidationError):
            # test4.test5.a must exist
            validator.validate({
                'test1': {
                    'a': 1
                },
                'test4': {
                    'test5': None
                }
            })

        # test4.test5.a exists, shouldn't throw
        validator.validate({
            'test1': {
                'a': 1
            },
            'test4': {
                'test5': {'a': 1}
            }
        })

    def test_type_validation(self):
        def type_test(param):
            def type_test2(p):
                self.assertEqual(p, param)
                return p

            return type_test2

        validator = dschema.Validator({
            'a': {
                'b': dschema.prop(type=int)
            },
            'c': {
                'd': 'int'
            },
            'e': 'test_validate',
            'f': type_test('test2'),
            'dict': dschema.Dict
        })

        validator.add_type('int', int)

        validator.add_type('test_validate', type_test('test1'))

        result = validator.validate({
            'a': {'b': 1},
            'c': {'d': 2},
            'e': 'test1',
            'f': 'test2',
            'dict': {'a': 'b'}
        })

        self.assertEqual(result['a']['b'], 1)
        self.assertEqual(result['c']['d'], 2)
        self.assertEqual(result['e'], 'test1')
        self.assertEqual(result['f'], 'test2')
