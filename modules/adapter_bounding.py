# adapter_bounding.py

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple

@dataclass(frozen=True)
class State:
    data: Any

class AdapterBounding:
    """
    Generic Adapter & Bounding.

    Users supply:
      - impl_cls            : the class under test
      - constructor_args    : args to build impl_cls()
      - constructor_kwargs  : kwargs to build impl_cls()
      - actions             : list of { name, params, label, guard }
      - snapshot_fn         : Callable(inst) -> hashable state
      - load_fn             : Callable(inst, state) -> None
      - bounds              : any user metadata
    """

    def __init__(
        self,
        impl_cls: Any,
        constructor_args: Tuple[Any, ...],
        constructor_kwargs: Dict[str, Any],
        actions: List[Dict[str, Any]],
        snapshot_fn: Callable[[Any], Any],
        load_fn: Callable[[Any, Any], None],
        bounds: Dict[str, Any] = None
    ):
        self.impl_cls      = impl_cls
        self.cargs         = constructor_args
        self.ckwargs       = constructor_kwargs
        self.actions       = actions
        self.snapshot_fn   = snapshot_fn
        self.load_fn       = load_fn
        self.bounds        = bounds or {}

    def initial_states(self) -> Iterable[State]:
        inst      = self.impl_cls(*self.cargs, **self.ckwargs)
        snapshot  = self.snapshot_fn(inst)
        yield State(data=snapshot)

    def successors(self, state: State) -> Iterable[Tuple[State, Set[str]]]:
        # Rehydrate instance
        base = self.impl_cls(*self.cargs, **self.ckwargs)
        self.load_fn(base, state.data)

        for action in self.actions:
            name   = action['name']
            params = action.get('params', [()])
            label  = action.get('label', name)
            guard  = action.get('guard', lambda inst, args: True)

            for args in params:
                if not guard(base, args):
                    continue

                # Fresh instance for each transition
                inst = self.impl_cls(*self.cargs, **self.ckwargs)
                self.load_fn(inst, state.data)

                # Invoke action
                method = getattr(inst, name)
                try:
                    method(*args)
                except Exception:
                    continue

                # Record next state
                next_snap = self.snapshot_fn(inst)
                yield State(data=next_snap), {label}
