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
from typing import List, Dict, Tuple, Optional
from hidet.ir.expr import Expr
from hidet.ir.type import FuncType, DataType, data_type
from hidet.ir.utils.type_utils import numeric_promotion
from hidet.ir.primitives.func import register_primitive_function, lookup_primitive_function


class MathFunctionSet:
    # cast function
    def cast(self, a: Expr, cast_dtype: DataType) -> Optional[Expr]:
        """
        Cast expression a to cast_dtype.

        If the default implementation is used, return None. The default implementation is to use the cast expression
        in the underlying language (e.g. C cast):
          (cast_dtype)(a)

        Parameters
        ----------
        a: Expr
            The expression to be cast.

        cast_dtype: DataType
            The target data type.

        Returns
        -------
        ret:
            The cast expression. None if (cast_dtype)(a) is used to represent the cast.
        """
        return None

    def make_vector(self, *items: Expr) -> Expr:
        """
        Make a vector-type value from a list of sub-expressions.

        For example, if we want to create a f16x2 type given two f16 expressions, we can use the following code:
            f16x2_expr = make_vector([f16_expr1, f16_expr2])

        Parameters
        ----------
        *items: Expr
            The list of sub-expressions.

        Returns
        -------
        ret: Expr
            The vector-type value. The number of lanes is determined by the length of the list.
        """
        raise NotImplementedError()

    def make_vector_from_scalar(self, scalar: Expr, num_lanes: int) -> Expr:
        raise NotImplementedError()

    # unary math functions
    def sin(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def cos(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def tan(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def sinh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def cosh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def tanh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def asin(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def acos(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def atan(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def asinh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def acosh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def atanh(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def exp(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def expm1(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def erf(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def sqrt(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def rsqrt(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def log(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def log2(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def log10(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def log1p(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def round(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def abs(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def trunc(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def ceil(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def floor(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def isfinite(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def isinf(self, a: Expr) -> Expr:
        raise NotImplementedError()

    def isnan(self, a: Expr) -> Expr:
        raise NotImplementedError()

    # binary math functions
    def min(self, a: Expr, b: Expr) -> Expr:
        raise NotImplementedError()

    def max(self, a: Expr, b: Expr) -> Expr:
        raise NotImplementedError()

    def mod(self, a: Expr, b: Expr) -> Expr:
        raise NotImplementedError()

    def pow(self, a: Expr, b: Expr) -> Expr:
        raise NotImplementedError()

    def atan2(self, a: Expr, b: Expr) -> Expr:
        raise NotImplementedError()

    # ternary math functions
    def fma(self, a: Expr, b: Expr, c: Expr) -> Expr:
        raise NotImplementedError()


# (device, dtype) -> math function set
# such as ('cuda', 'float16') -> MathFunctionSet
registered_math_function_sets: Dict[Tuple[str, str], MathFunctionSet] = {}


def register_math_function_set(device: str, dtype: str, math_function_set: MathFunctionSet):
    if (device, dtype) in registered_math_function_sets:
        raise ValueError(f"Math function set for {device} and {dtype} already registered")
    registered_math_function_sets[(device, dtype)] = math_function_set


def type_infer_func(arg_types: List[DataType]) -> DataType:
    dtype = arg_types[0]
    for arg_type in arg_types[1:]:
        dtype = numeric_promotion(dtype, arg_type)
    return dtype


def tif_make_vector(arg_types: List[DataType]) -> DataType:
    from hidet.ir.dtypes import vectorize

    if len(arg_types) == 0:
        raise ValueError("At least one argument is required")
    if not all(arg_types[0] == arg_type for arg_type in arg_types[1:]):
        raise ValueError("All arguments must have the same type")
    return vectorize(arg_types[0], len(arg_types))


class MathFunctionSetGeneric(MathFunctionSet):
    @staticmethod
    def register():
        unary_names = [
            'sin',
            'cos',
            'tan', # changed file path: hidet.ir.primitives.math.py
            'tanh',
            'exp',
            'round',
            'abs',
            'floor',
            'ceil',
            'sqrt',
            'rsqrt',
            'erf',
            'log',
            'log2',
            'log10',
            'log1p',
            'trunc',
            'isfinite',
            'isinf',
            'isnan',
            'make_vector',
        ]
        binary_names = ['min', 'max', 'pow', 'mod', 'atan2']
        ternary_names = ['fma']
        for name in unary_names + binary_names + ternary_names:
            if name in ['isfinite', 'isinf', 'isnan']:
                func_type = FuncType(type_infer_func=lambda _: data_type('bool'))
            elif name == 'make_vector':
                func_type = FuncType(type_infer_func=tif_make_vector)
            else:
                func_type = FuncType(type_infer_func=type_infer_func)
            register_primitive_function(name=f'generic_{name}', codegen_name=None, func_or_type=func_type, generic=True)

    @staticmethod
    def call(name, *args) -> Expr:
        entry = lookup_primitive_function(f'generic_{name}')
        return entry.var(*args)

    # unary names

    def sin(self, a: Expr) -> Expr:
        return self.call('sin', a)

    def cos(self, a: Expr) -> Expr:
        return self.call('cos', a)

    def tan(self, a: Expr) -> Expr:
        return self.call('tan', a)

    def sinh(self, a: Expr) -> Expr:
        return self.call('sinh', a)

    def cosh(self, a: Expr) -> Expr:
        return self.call('cosh', a)

    def tanh(self, a: Expr) -> Expr:
        return self.call('tanh', a)

    def asin(self, a: Expr) -> Expr:
        return self.call('asin', a)

    def acos(self, a: Expr) -> Expr:
        return self.call('acos', a)

    def atan(self, a: Expr) -> Expr:
        return self.call('atan', a)

    def asinh(self, a: Expr) -> Expr:
        return self.call('asinh', a)

    def acosh(self, a: Expr) -> Expr:
        return self.call('acosh', a)

    def atanh(self, a: Expr) -> Expr:
        return self.call('atanh', a)

    def exp(self, a: Expr) -> Expr:
        return self.call('exp', a)

    def expm1(self, a: Expr) -> Expr:
        return self.call('expm1', a)

    def erf(self, a: Expr) -> Expr:
        return self.call('erf', a)

    def sqrt(self, a: Expr) -> Expr:
        return self.call('sqrt', a)

    def rsqrt(self, a: Expr) -> Expr:
        return self.call('rsqrt', a)

    def log(self, a: Expr) -> Expr:
        return self.call('log', a)

    def log2(self, a: Expr) -> Expr:
        return self.call('log2', a)

    def log10(self, a: Expr) -> Expr:
        return self.call('log10', a)

    def log1p(self, a: Expr) -> Expr:
        return self.call('log1p', a)

    def round(self, a: Expr) -> Expr:
        return self.call('round', a)

    def abs(self, a: Expr) -> Expr:
        return self.call('abs', a)

    def ceil(self, a: Expr) -> Expr:
        return self.call('ceil', a)

    def floor(self, a: Expr) -> Expr:
        return self.call('floor', a)

    def trunc(self, a: Expr) -> Expr:
        return self.call('trunc', a)

    def isfinite(self, a: Expr) -> Expr:
        return self.call('isfinite', a)

    def isinf(self, a: Expr) -> Expr:
        return self.call('isinf', a)

    def isnan(self, a: Expr) -> Expr:
        return self.call('isnan', a)

    # binary names

    def atan2(self, a: Expr, b: Expr) -> Expr:
        return self.call('atan2', a, b)

    def min(self, a: Expr, b: Expr) -> Expr:
        return self.call('min', a, b)

    def max(self, a: Expr, b: Expr) -> Expr:
        return self.call('max', a, b)

    def mod(self, a: Expr, b: Expr) -> Expr:
        return self.call('mod', a, b)

    def pow(self, a: Expr, b: Expr) -> Expr:
        return self.call('pow', a, b)

    # ternary names

    def fma(self, a: Expr, b: Expr, c: Expr) -> Expr:
        return self.call('fma', a, b, c)

    def make_vector(self, *args) -> Expr:
        return self.call('make_vector', *args)


generic_math_function_set = MathFunctionSetGeneric()
generic_math_function_set.register()


def sin(a: Expr) -> Expr:
    return generic_math_function_set.sin(a)


def cos(a: Expr) -> Expr:
    return generic_math_function_set.cos(a)


def tan(a: Expr) -> Expr:
    return generic_math_function_set.tan(a)


def sinh(a: Expr) -> Expr:
    return generic_math_function_set.sinh(a)


def cosh(a: Expr) -> Expr:
    return generic_math_function_set.cosh(a)


def tanh(a: Expr) -> Expr:
    return generic_math_function_set.tanh(a)


def asin(a: Expr) -> Expr:
    return generic_math_function_set.asin(a)


def acos(a: Expr) -> Expr:
    return generic_math_function_set.acos(a)


def atan(a: Expr) -> Expr:
    return generic_math_function_set.atan(a)


def atan2(a: Expr, b: Expr) -> Expr:
    return generic_math_function_set.atan2(a, b)


def asinh(a: Expr) -> Expr:
    return generic_math_function_set.asinh(a)


def acosh(a: Expr) -> Expr:
    return generic_math_function_set.acosh(a)


def atanh(a: Expr) -> Expr:
    return generic_math_function_set.atanh(a)


def exp(a: Expr) -> Expr:
    return generic_math_function_set.exp(a)


def expm1(a: Expr) -> Expr:
    return generic_math_function_set.expm1(a)


def erf(a: Expr) -> Expr:
    return generic_math_function_set.erf(a)


def sqrt(a: Expr) -> Expr:
    return generic_math_function_set.sqrt(a)


def rsqrt(a: Expr) -> Expr:
    return generic_math_function_set.rsqrt(a)


def log(a: Expr) -> Expr:
    return generic_math_function_set.log(a)


def log2(a: Expr) -> Expr:
    return generic_math_function_set.log2(a)


def log10(a: Expr) -> Expr:
    return generic_math_function_set.log10(a)


def log1p(a: Expr) -> Expr:
    return generic_math_function_set.log1p(a)


def round(a: Expr) -> Expr:
    return generic_math_function_set.round(a)


def abs(a: Expr) -> Expr:
    return generic_math_function_set.abs(a)


def ceil(a: Expr) -> Expr:
    return generic_math_function_set.ceil(a)


def floor(a: Expr) -> Expr:
    return generic_math_function_set.floor(a)


def trunc(a: Expr) -> Expr:
    return generic_math_function_set.trunc(a)


def min(a: Expr, b: Expr) -> Expr:
    return generic_math_function_set.min(a, b)


def max(a: Expr, b: Expr) -> Expr:
    return generic_math_function_set.max(a, b)


def mod(a: Expr, b: Expr) -> Expr:
    return generic_math_function_set.mod(a, b)


def pow(a: Expr, b: Expr) -> Expr:
    return generic_math_function_set.pow(a, b)


def fma(a: Expr, b: Expr, c: Expr) -> Expr:
    return generic_math_function_set.fma(a, b, c)


def isfinite(a: Expr) -> Expr:
    return generic_math_function_set.isfinite(a)


def isinf(a: Expr) -> Expr:
    return generic_math_function_set.isinf(a)


def isnan(a: Expr) -> Expr:
    return generic_math_function_set.isnan(a)


def make_vector(*args) -> Expr:
    return generic_math_function_set.make_vector(*args)
