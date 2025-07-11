# modules/property_extraction.py

import importlib
from typing import Dict, List, Tuple, Any
from pyModelChecking.CTL.language import Formula

class PropertyExtraction:
    """
    Load user‐specified CTL properties from a Python module and
    validate them against the scoped contract interface, organizing
    them into 'safety' and 'liveness' lists of (name, FormulaAST).
    """

    def __init__(self, scope: Dict[str, Any], properties_module: str):
        """
        :param scope: dict from ScopeDefinition.extract_scope()
        :param properties_module: Python module path (e.g. "config.properties")
                                  which must export a `properties` dict of the form:
                                  {
                                    "safety":   [(name, FormulaAST), …],
                                    "liveness": [(name, FormulaAST), …]
                                  }
        """
        self.scope = scope
        self.fn_names = { fn["name"] for fn in scope["functions"] }

        # Dynamically import the user‐provided properties module
        mod = importlib.import_module(properties_module)
        if not hasattr(mod, "properties"):
            raise ValueError(f"Module {properties_module!r} must define a `properties` dict")
        self.user_props = mod.properties

    def extract_properties(self) -> Dict[str, List[Tuple[str, Formula]]]:
        """
        Returns a dict:
          {
            "safety":   [(name, FormulaAST), …],
            "liveness": [(name, FormulaAST), …]
          }
        """
        categorized: Dict[str, List[Tuple[str, Formula]]] = {"safety": [], "liveness": []}

        for cat in ("safety", "liveness"):
            if cat not in self.user_props:
                raise ValueError(f"`properties` module missing required category '{cat}'")
            for item in self.user_props[cat]:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise ValueError(f"Invalid entry in properties['{cat}']: {item!r}")
                name, phi = item
                # Basic checks:
                if not isinstance(name, str):
                    raise ValueError(f"Property name must be a string, got {name!r}")
                if not hasattr(phi, "__class__") or not hasattr(phi, "wrap_subformulas"):
                    # crude check for CTL AST
                    raise ValueError(f"Property formula for '{name}' is not a CTL Formula AST")
                categorized[cat].append((name, phi))

        return categorized
