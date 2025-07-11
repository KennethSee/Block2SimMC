from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple

@dataclass(frozen=True)
class State:
    """A hashable wrapper around whatever snapshot_fn returns."""
    data: Any

class AdapterBounding:
    """
    A minimal Adapter & Bounding.

    :param impl_cls:       class under test (must have a no-arg constructor)
    :param snapshot_fn:    fn(inst) -> hashable state
    :param load_fn:        fn(inst, state) -> None
    :param method_bounds:  dict of
        method_name -> {
          'args_generator': Callable[[], Iterable[Tuple]], 
          'label':          Optional[str]
        }
    """

    def __init__(
        self,
        impl_cls: Any,
        snapshot_fn: Callable[[Any], Any],
        load_fn:     Callable[[Any, Any], None],
        method_bounds: Dict[str, Dict[str, Any]]
    ):
        self.impl_cls      = impl_cls
        self.snapshot_fn   = snapshot_fn
        self.load_fn       = load_fn
        self.method_bounds = method_bounds

    def initial_states(self) -> Iterable[State]:
        inst     = self.impl_cls()
        snap     = self.snapshot_fn(inst)
        yield State(snap)

    def successors(self, state: State) -> Iterable[Tuple[State, Set[str]]]:
        base = self.impl_cls()
        self.load_fn(base, state.data)

        for method_name, cfg in self.method_bounds.items():
            gen    = cfg['args_generator']
            label  = cfg.get('label', method_name)
            guard  = cfg.get('guard', lambda inst,args: True)

            for args in gen():
                # apply guard *before* rehydrating for performance
                if not guard(base, args):
                    continue

                inst = self.impl_cls()
                self.load_fn(inst, state.data)
                try:
                    getattr(inst, method_name)(*args)
                except Exception:
                    continue

                new_snap = self.snapshot_fn(inst)
                yield State(new_snap), {label}
