from typing import Dict, List, Tuple, Set, Any
import pyModelChecking.CTL as CTL
from pyModelChecking.kripke import Kripke

class ModelChecker:
    def __init__(self, model: Any):
        self.model  = model
        self.kripke = self._to_kripke(model)

    def _to_kripke(self, m: Any) -> Kripke:
        S  = list(m.states)
        S0 = list(m.initial)

        R = []
        L_labels = { s:set() for s in S }
        for s, outs in m.transitions.items():
            for (s2, labels) in outs:
                R.append((s, s2))
                L_labels[s2].update(labels)

        # make R total
        sources = { u for (u,_) in R }
        for s in S:
            if s not in sources:
                R.append((s, s))

        return Kripke(S=S, S0=S0, R=R, L=L_labels)

    def check(
        self,
        properties: Dict[str, List[Tuple[str, str]]]
    ) -> Dict[str, bool]:
        """
        :param properties: {
            "safety":   [(name, formula), ...],
            "liveness": [(name, formula), ...]
        }
        where each formula is a CTL state‐formula string, e.g.
          "AG ( dequeue -> AX not dequeue )"
        """
        results: Dict[str,bool] = {}

        for category, props in properties.items():
            for name, phi in props:
                # modelcheck will parse the CTL string internally
                sat = CTL.modelcheck(self.kripke, phi)
                # passes if *all* initial states satisfy it
                results[name] = self.kripke.S0.issubset(sat)

        return results
