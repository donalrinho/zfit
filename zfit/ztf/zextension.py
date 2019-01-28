import math as _mt

from typing import Any

try:
    from math import inf as _inf
except ImportError:  # py34 remove try-except
    _inf = float('inf')

import tensorflow as tf
from ..settings import ztypes

inf = tf.constant(_inf, dtype=ztypes.float)


def constant(value, dtype=ztypes.float, shape=None, name="Const", verify_shape=False):
    return tf.constant(value, dtype=dtype, shape=shape, name=name, verify_shape=verify_shape)


pi = constant(_mt.pi)


def to_complex(number, dtype=ztypes.complex):
    return tf.cast(number, dtype=dtype)


def to_real(x, dtype=ztypes.float):
    return tf.cast(x, dtype=dtype)


def abs_square(x):
    return tf.real(x * tf.conj(x))


def nth_pow(x, n, name=None):
    """Calculate the nth power of the complex Tensor x.

    Args:
        x (tf.Tensor, complex):
        n (int >= 0): Power
        name (str): No effect, for API compatibility with tf.pow
    """
    if not n >= 0:
        raise ValueError("n (power) has to be >= 0. Currently, n={}".format(n))

    power = to_complex(1.)
    for _ in range(n):
        power *= x
    return power


def unstack_x(value: Any, num: Any = None, axis: int = -1, name: str = "unstack_x"):
    if isinstance(value, list):
        return value
    unstacked_x = tf.unstack(value=value, num=num, axis=axis, name=name)
    if len(unstacked_x) == 1:
        unstacked_x = unstacked_x[0]
    return unstacked_x


def stack_x(values, axis: int = -1, name: str = "stack_x"):
    return tf.stack(values=values, axis=axis, name=name)


# random sampling


def convert_to_tensor(value, dtype=None, name=None, preferred_dtype=None):
    return tf.convert_to_tensor(value=value, dtype=dtype, name=name, preferred_dtype=preferred_dtype)

# reduce functions
