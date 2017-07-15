# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2017 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

from hypothesis.errors import InvalidArgument
from hypothesis.searchstrategy.strategies import SearchStrategy


class DeferredStrategy(SearchStrategy):

    """A strategy which may be used before it is fully defined."""

    def __init__(self):
        SearchStrategy.__init__(self)
        self.__wrapped_strategy = None
        self.__in_repr = False
        self.__is_empty = None

    @property
    def supports_find(self):
        if self.__wrapped_strategy is None:
            return True
        else:
            return self.__wrapped_strategy.supports_find

    @property
    def is_empty(self):
        if self.__wrapped_strategy is None:
            return False
        if self.__is_empty is None:
            # This is not an error. We set __is_empty to be False so that we
            # if the wrapped strategy ends up calling in_empty here recursively
            # then we don't recurse. We then set it to a more accurate answer
            # afterwards. There are a bunch of cases this won't detect, but
            # in_empty is always intended to be a conservative approximation
            # so that's fine.
            self.__is_empty = False
            self.__is_empty = self.__wrapped_strategy.is_empty
        return self.__is_empty

    def __repr__(self):
        if self.__wrapped_strategy is not None and not self.__in_repr:
            try:
                self.__in_repr = True
                return repr(self.__wrapped_strategy)
            finally:
                self.__in_repr = False
        else:
            return 'deferred()'

    def define(self, definition):
        if not isinstance(definition, SearchStrategy):
            raise InvalidArgument((
                'Expected definition to be SearchStrategy but got %r of '
                'type %s') % (
                definition, type(definition).__name__
            ))

        if definition is self:
            raise InvalidArgument(
                'Cannot define a deferred strategy to be itself!'
            )
        if self.__wrapped_strategy is not None:
            raise InvalidArgument((
                'Deferred strategy has already been defined as %r. Cannot '
                'redefine it as %r.'
            ) % (self.__wrapped_strategy, definition))
        else:
            self.__wrapped_strategy = definition

    def do_draw(self, data):
        if self.__wrapped_strategy is None:
            raise InvalidArgument(
                'Attempted to draw from deferred strategy that has not yet '
                'been defined.'
            )
        else:
            return self.__wrapped_strategy.do_draw(data)
