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

"""Types used by neuralgcm.experimental API."""
import dataclasses
from typing import Any, Callable, Generic, TypeVar

import jax
import jax.numpy as jnp
from neuralgcm.experimental import scales
import numpy as np
import tree_math


#
# Generic types.
#
Dtype = jax.typing.DTypeLike | Any
Array = np.ndarray | jax.Array
Numeric = float | int | Array
Timestep = np.timedelta64 | float
PRNGKeyArray = jax.Array
units = scales.units
Quantity = scales.Quantity

#
# Generic API input/output types.
#
PyTreeState = TypeVar('PyTreeState')
Pytree = Any


@tree_math.struct
class ModelState(Generic[PyTreeState]):
  """Simulation state decomposed into prognostic, diagnostic and randomness.

  Attributes:
    prognostics: Prognostic variables describing the simulation state.
    diagnostics: Optional diagnostic values holding diagnostic information.
    randomness: Optional randomness state describing stochasticity of the model.
  """

  prognostics: PyTreeState
  diagnostics: Pytree = dataclasses.field(default_factory=dict)
  randomness: Pytree = dataclasses.field(default_factory=dict)


@jax.tree_util.register_pytree_node_class
@dataclasses.dataclass
class Randomness:
  """State describing the random process."""

  prng_key: jax.Array
  prng_step: int = 0
  core: Pytree = None

  def tree_flatten(self):
    """Flattens Randomness JAX pytree."""
    leaves = (self.prng_key, self.prng_step, self.core)
    aux_data = ()
    return leaves, aux_data

  @classmethod
  def tree_unflatten(cls, aux_data, leaves):
    """Unflattens Randomness from aux_data and leaves."""
    return cls(*leaves, *aux_data)


@jax.tree_util.register_pytree_node_class
@dataclasses.dataclass
class Timedelta:
  """JAX compatible time duration, stored in days and seconds.

  Like datetime.timedelta, seconds are always normalized to fall in the range
  [0, 24 * 60 * 60).

  Using integer days and seconds is recommended to avoid loss of precision. With
  int32 days, Timedelta can exactly represent durations over 5 million years.
  """

  days: Numeric = 0
  seconds: Numeric = 0

  def __post_init__(self):
    days_delta, seconds = divmod(self.seconds, 24 * 60 * 60)
    self.days = self.days + days_delta
    self.seconds = seconds

  def __add__(self, other):
    if type(other) is not Timedelta:  # pylint: disable=unidiomatic-typecheck
      return NotImplemented
    days = self.days + other.days
    seconds = self.seconds + other.seconds
    return Timedelta(days, seconds)

  def __mul__(self, other):
    if not isinstance(other, Numeric):
      return NotImplemented
    return Timedelta(self.days * other, self.seconds * other)

  __rmul__ = __mul__

  # TODO(shoyer): consider adding other methods supported by datetime.timedelta.

  def tree_flatten(self):
    leaves = (self.days, self.seconds)
    aux_data = None
    return leaves, aux_data

  @classmethod
  def tree_unflatten(cls, aux_data, leaves):
    assert aux_data is None
    return cls(*leaves)


#
# API function signatures.
#
PostProcessFn = Callable[..., Any]


#
# Auxiliary types for intermediate computations.
#
@dataclasses.dataclass(eq=True, order=True, frozen=True)
class KeyWithCosLatFactor:
  """Class describing a key by `name` and an integer `factor_order`."""

  name: str
  factor_order: int
