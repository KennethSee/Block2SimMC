import json

class PropertyExtraction:
    """
    Load user-specified temporal properties and validate them
    against the scoped contract interface, organizing them into
    'safety' (including ordering) and 'liveness'.
    """

    def __init__(self, scope, properties_file):
        """
        :param scope: dict from ScopeDefinition.extract_scope()
        :param properties_file: JSON file defining properties
        """
        self.scope = scope
        with open(properties_file) as f:
            # expect list of { name, category, formula }
            self.user_props = json.load(f)

        self.fn_names = { fn["name"] for fn in scope["functions"] }

    def extract_properties(self):
        """
        Returns a dict:
          {
            "safety":   [(name, formula), …],
            "liveness": [(name, formula), …]
          }
        """
        categorized = {"safety": [], "liveness": []}
        for prop in self.user_props:
            name     = prop["name"]
            cat      = prop["category"]   # 'safety' or 'liveness'
            formula  = prop["formula"]

            # Basic check: ensure any referenced function exists
            if not any(fn in formula for fn in self.fn_names):
                raise ValueError(f"Property '{name}' references unknown symbols")

            if cat not in categorized:
                raise ValueError(f"Unknown category '{cat}' for property '{name}'")
            categorized[cat].append((name, formula))

        return categorized
