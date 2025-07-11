from dataclasses import dataclass
from typing import (
    Any, Callable, Dict, Iterable,
    List, Optional, Set, Tuple, Union
)
from .adapter_bounding import State, AdapterBounding

@dataclass
class Model:
    """
    A simple explicit-state model.
    """
    states: Set[Any]                                   # State or (State,State)
    initial: Set[Any]                                  # subset of states
    transitions: Dict[Any, List[Tuple[Any, Set[str]]]] # origin -> [(dest, labels)]

class ModelBuilder:
    """
    Build an explicit-state model from one or two adapters.

    If two adapters are given, eq_fn(s1,s2) decides which pairs are
    considered equivalent (and therefore explored).
    """

    def __init__(
        self,
        adapters: List[AdapterBounding],
        eq_fn: Optional[Callable[[State, State], bool]] = None
    ):
        if not 1 <= len(adapters) <= 2:
            raise ValueError("Must supply 1 or 2 adapters")
        self.adapters = adapters
        # default eq_fn for single-adapter: ignore, pair states by identity
        self.eq_fn = eq_fn or (lambda s1, s2: s1.data == s2.data)

    def build(self) -> Model:
        if len(self.adapters) == 1:
            return self._build_single(self.adapters[0])
        return self._build_joint(self.adapters[0], self.adapters[1])

    def _build_single(self, adapter: AdapterBounding) -> Model:
        states       = set()      # Set[State]
        initial      = set(adapter.initial_states())
        transitions  = {}
        work         = list(initial)
        states |= initial

        while work:
            s = work.pop()
            transitions.setdefault(s, [])
            for (ns, labels) in adapter.successors(s):
                transitions[s].append((ns, labels))
                if ns not in states:
                    states.add(ns)
                    work.append(ns)

        return Model(states=states, initial=initial, transitions=transitions)

    def _build_joint(
        self,
        ad1: AdapterBounding,
        ad2: AdapterBounding
    ) -> Model:
        # States are pairs (s1, s2)
        states      = set()      # Set[Tuple[State,State]]
        initial     = set()
        transitions = {}

        # initialise with all equivalent pairs of initial states
        for s1 in ad1.initial_states():
            for s2 in ad2.initial_states():
                if self.eq_fn(s1, s2):
                    pair = (s1, s2)
                    states.add(pair)
                    initial.add(pair)

        work = list(initial)
        while work:
            (s1, s2) = work.pop()
            transitions.setdefault((s1, s2), [])
            for (ns1, lbls1) in ad1.successors(s1):
                for (ns2, lbls2) in ad2.successors(s2):
                    if self.eq_fn(ns1, ns2):
                        pair_next = (ns1, ns2)
                        transitions[(s1, s2)].append((pair_next, lbls1 | lbls2))
                        if pair_next not in states:
                            states.add(pair_next)
                            work.append(pair_next)

        return Model(states=states, initial=initial, transitions=transitions)
