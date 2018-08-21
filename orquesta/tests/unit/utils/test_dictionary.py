# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import unittest

from orquesta.utils import dictionary as utils


LEFT = {
    'k1': '123',
    'k2': 'abc',
    'k3': {
        'k31': True,
        'k32': 1.0
    }
}

RIGHT = {
    'k2': 'def',
    'k3': {
        'k32': 2.0,
        'k33': {
            'k331': 'foo'
        }
    },
    'k4': 'bar'
}


class DictUtilsTest(unittest.TestCase):

    def test_dict_merge_overwrite(self):
        left = copy.deepcopy(LEFT)
        right = copy.deepcopy(RIGHT)

        utils.merge_dicts(left, right)

        expected = {
            'k1': '123',
            'k2': 'def',
            'k3': {
                'k31': True,
                'k32': 2.0,
                'k33': {
                    'k331': 'foo'
                }
            },
            'k4': 'bar'
        }

        self.assertDictEqual(left, expected)

    def test_dict_merge_overwrite_false(self):
        left = copy.deepcopy(LEFT)
        right = copy.deepcopy(RIGHT)

        utils.merge_dicts(left, right, overwrite=False)

        expected = {
            'k1': '123',
            'k2': 'abc',
            'k3': {
                'k31': True,
                'k32': 1.0,
                'k33': {
                    'k331': 'foo'
                }
            },
            'k4': 'bar'
        }

        self.assertDictEqual(left, expected)

    def test_dict_dot_notation_access(self):
        data = {
            'a': 'foo',
            'b': {
                'c': 'bar',
                'd': {
                    'e': 123,
                    'f': False,
                    'g': {},
                    'h': None
                }
            },
            'x': {},
            'y': None
        }

        self.assertEqual('foo', utils.get_dict_value(data, 'a'))
        self.assertEqual('bar', utils.get_dict_value(data, 'b.c'))
        self.assertEqual(123, utils.get_dict_value(data, 'b.d.e'))
        self.assertFalse(utils.get_dict_value(data, 'b.d.f'))
        self.assertDictEqual({}, utils.get_dict_value(data, 'b.d.g'))
        self.assertIsNone(utils.get_dict_value(data, 'b.d.h'))
        self.assertDictEqual({}, utils.get_dict_value(data, 'x'))
        self.assertIsNone(utils.get_dict_value(data, 'x.x'))
        self.assertIsNone(utils.get_dict_value(data, 'y'))
        self.assertIsNone(utils.get_dict_value(data, 'z'))

    def test_dict_dot_notation_access_type_error(self):
        data = {'a': 'foo'}

        self.assertRaises(
            TypeError,
            utils.get_dict_value,
            data,
            'a.b'
        )

    def test_dict_dot_notation_access_key_error(self):
        data = {'a': {}}

        self.assertRaises(
            KeyError,
            utils.get_dict_value,
            data,
            'a.b',
            raise_key_error=True
        )