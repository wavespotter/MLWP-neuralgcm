# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from absl.testing import absltest
import jax
from neuralgcm.experimental import typing


class TimedeltaTest(absltest.TestCase):

  def test_defaults(self):
    actual = typing.Timedelta()
    expected = typing.Timedelta(0, 0)
    self.assertEqual(actual, expected)

  def test_normalization(self):
    actual = typing.Timedelta(0, 24 * 60 * 60)
    expected = typing.Timedelta(1, 0)
    self.assertEqual(actual, expected)

    actual = typing.Timedelta(0, -1)
    expected = typing.Timedelta(-1, 86399)
    self.assertEqual(actual, expected)

  def test_addition(self):
    delta = typing.Timedelta(1, 12 * 60 * 60)
    actual = delta + delta
    expected = typing.Timedelta(3, 0)
    self.assertEqual(actual, expected)

    with self.assertRaises(TypeError):
      expected + 60

  def test_multiplication(self):
    delta = typing.Timedelta(1, 12 * 60 * 60)
    expected = typing.Timedelta(3, 0)

    actual = delta * 2
    self.assertEqual(actual, expected)

    actual = 2 * delta
    self.assertEqual(actual, expected)

    with self.assertRaises(TypeError):
      delta * delta

  def test_pytree(self):
    delta = typing.Timedelta(1, 12 * 60 * 60)
    expected = typing.Timedelta(3, 0)
    actual = jax.tree.map(lambda x: 2 * x, delta)
    self.assertEqual(actual, expected)


if __name__ == "__main__":
  absltest.main()
