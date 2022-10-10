"""
Author: lpdink
Date: 2022-10-09 10:46:26
LastEditors: lpdink
LastEditTime: 2022-10-10 07:02:21
Description: Reference from https://github.com/edgedb/edgedb/blob/master/edb/common/value_dispatch.py, thanks to the EdgeDB.
做了更改，将匹配第一个参数更改为匹配第二个参数，以应用在成员函数中。
"""
#
# This source file is part of the EdgeDB open source project.
#
# Copyright 2021-present MagicStack Inc. and the EdgeDB authors.
#
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
#


import functools


def value_dispatch(func):
    """Like singledispatch() but dispatches by value of the second arg.

    Example:

      @value_dispatch
      def eat(self, fruit):
          return f"I don't want a {fruit}..."

      @eat.register('apple')
      def _eat_apple(self, fruit):
          return "I love apples!"

      @eat.register('eggplant')
      @eat.register('squash')
      def _eat_what(self, fruit):
          return f"I didn't know {fruit} is a fruit!"

    An alternative to applying multuple `register` decorators is to
    use the `register_for_all` helper:

      @eat.register_for_all({'eggplant', 'squash'})
      def _eat_what(self, fruit):
          return f"I didn't know {fruit} is a fruit!"
    """

    registry = {}

    @functools.wraps(func)
    def wrapper(arg0, arg1, *args, **kwargs):
        try:
            delegate = registry[arg1]
        except KeyError:
            pass
        else:
            return delegate(arg0, arg1, *args, **kwargs)

        return func(arg0, arg1, *args, **kwargs)

    def register(value):
        def wrap(func):
            if value in registry:
                raise ValueError(
                    f"@value_dispatch: there is already a handler "
                    f"registered for {value!r}"
                )
            registry[value] = func
            return func

        return wrap

    def register_for_all(values):
        def wrap(func):
            for value in values:
                if value in registry:
                    raise ValueError(
                        f"@value_dispatch: there is already a handler "
                        f"registered for {value!r}"
                    )
                registry[value] = func
            return func

        return wrap

    wrapper.register = register
    wrapper.register_for_all = register_for_all
    return wrapper
