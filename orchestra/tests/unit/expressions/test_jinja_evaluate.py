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

from orchestra import exceptions as exc
from orchestra.expressions import jinja
from orchestra.tests.unit import base
from orchestra.utils import plugin


class JinjaEvaluationTest(base.ExpressionEvaluatorTest):

    @classmethod
    def setUpClass(cls):
        cls.language = 'jinja'
        super(JinjaEvaluationTest, cls).setUpClass()

    def test_get_evaluator(self):
        e = plugin.get_module(
            'orchestra.expressions.evaluators',
            self.language
        )

        self.assertEqual(e, jinja.JinjaEvaluator)
        self.assertIn('json', e._custom_functions.keys())
        self.assertIn('task_state', e._custom_functions.keys())

    def test_basic_eval(self):
        expr = '{{ _.foo }}'

        data = {'foo': 'bar'}

        self.assertEqual('bar', self.evaluator.evaluate(expr, data))

    def test_basic_bad_eval(self):
        expr = '{{ _.foo }}'

        data = {}

        self.assertRaises(
            exc.JinjaEvaluationException,
            self.evaluator.evaluate,
            expr,
            data
        )

    def test_nested_eval(self):
        expr = '{{ _.nested.foo }}'

        data = {
            'nested': {
                'foo': 'bar'
            }
        }

        self.assertEqual('bar', self.evaluator.evaluate(expr, data))

    def test_multi_eval(self):
        expr = '{{ _.foo }} and {{ _.marco }}'

        data = {
            'foo': 'bar',
            'marco': 'polo'
        }

        self.assertEqual('bar and polo', self.evaluator.evaluate(expr, data))

    def test_eval_recursive(self):
        expr = '{{ _.fee }}'

        data = {
            'fee': '{{ _.fi }}',
            'fi': '{{ _.fo }}',
            'fo': '{{ _.fum }}',
            'fum': 'fee-fi-fo-fum'
        }

        self.assertEqual('fee-fi-fo-fum', self.evaluator.evaluate(expr, data))

    def test_multi_eval_recursive(self):
        expr = '{{ _.fee }} {{ _.im }}'

        data = {
            'fee': '{{ _.fi }} <_.fo }}',
            'fi': '{{ _.fo }}',
            'fo': '{{ _.fum }}',
            'fum': 'fee-fi-fo-fum!',
            'im': '{{ _.hungry }}',
            'hungry': 'i\'m hungry!'
        }

        self.assertEqual(
            'fee-fi-fo-fum! i\'m hungry!',
            self.evaluator.evaluate(expr, data)
        )

    def test_type_preservation(self):
        data = {
            'k1': 101,
            'k2': 1.999,
            'k3': True,
            'k4': [1, 2],
            'k5': {'k': 'v'},
            'k6': None
        }

        self.assertEqual(
            data['k1'],
            self.evaluator.evaluate('{{ _.k1 }}', data)
        )

        self.assertEqual(
            data['k2'],
            self.evaluator.evaluate('{{ _.k2 }}', data)
        )

        self.assertTrue(self.evaluator.evaluate('{{ _.k3 }}', data))

        self.assertListEqual(
            data['k4'],
            self.evaluator.evaluate('{{ _.k4 }}', data)
        )

        self.assertDictEqual(
            data['k5'],
            self.evaluator.evaluate('{{ _.k5 }}', data)
        )

        self.assertIsNone(self.evaluator.evaluate('{{ _.k6 }}', data))

    def test_type_string_detection(self):
        expr = '{{ _.foo }} -> {{ _.bar }}'

        data = {
            'foo': 101,
            'bar': 201
        }

        self.assertEqual('101 -> 201', self.evaluator.evaluate(expr, data))

    def test_custom_function(self):
        expr = '{{ json(\'{"a": 123}\') }}'

        self.assertDictEqual({'a': 123}, self.evaluator.evaluate(expr))

    def test_custom_function_failure(self):
        expr = '{{ json(int(123)) }}'

        self.assertRaises(
            exc.JinjaEvaluationException,
            self.evaluator.evaluate,
            expr
        )