from solidity_parser import parser
import json

class ScopeDefinition:

    def __init__(self, contract_file_path):
        self.contract_file_path = contract_file_path

    def extract_scope(self):
        ast = parser.parse_file(self.contract_file_path)
        scope = {
            "functions": [],
            "state_variables": []
        }
        for item in ast['children']:
            if item.get('type') == 'ContractDefinition':
                for sub in item['subNodes']:
                    if sub['type'] == 'FunctionDefinition' and sub.get('visibility') in ('public','external'):
                        # record function name and parameters
                        fn_name = sub.get('name') or ''
                        params = [(p['typeName']['name'], p['name']) for p in sub.get('parameters', {}).get('parameters', [])]
                        scope['functions'].append({'name': fn_name, 'params': params})
                    elif sub['type'] == 'VariableDeclaration' and sub.get('isStateVar'):
                        # record state variable name and type
                        scope['state_variables'].append({
                            'name': sub['name'],
                            'type': sub['typeName'].get('name') or sub['typeName'].get('baseTypeName', {}).get('name')
                        })
        return scope