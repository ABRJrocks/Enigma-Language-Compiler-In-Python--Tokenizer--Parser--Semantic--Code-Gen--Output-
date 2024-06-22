class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.memory_location = 1000

    def add_to_symbol_table(self, identifier, data_type, value=None):
        """Add a variable to the symbol table."""
        if identifier in self.symbol_table:
            raise ValueError(f"Variable '{identifier}' already declared")
        self.symbol_table[identifier] = {
            'data_type': data_type, 'value': value, 'memory_location': self.memory_location}
        self.memory_location += 4

    def check_variable_declaration(self, data_type, identifier, value):
        """Check the validity of a variable declaration."""
        if not identifier.startswith('v-'):
            raise ValueError("Variable names must start with 'v-'")
        if not identifier[2:].isalnum() or identifier[2].isdigit():
            raise ValueError("Invalid variable name")
        if data_type not in ['enum', 'efl', 'estr', 'ebool']:
            raise ValueError("Invalid data type")

    def analyze_code(self, tokens):
        """Perform semantic analysis on the code and build the symbol table."""
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token['type'] == 'DATATYPE':
                data_type = token['value']
                if i + 1 < len(tokens) and tokens[i + 1]['type'] == 'VARIABLE':
                    identifier = tokens[i + 1]['value']
                    i += 2
                    value = None
                    if i < len(tokens) and tokens[i]['type'] == 'ASSIGN':
                        if i + 1 < len(tokens) and tokens[i + 1]['type'] in ['NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE']:
                            value = tokens[i + 1]['value']
                            i += 1
                    self.check_variable_declaration(
                        data_type, identifier, value)
                    self.add_to_symbol_table(identifier, data_type, value)
            elif token['type'] == 'VARIABLE':
                identifier = token['value']
                if i + 1 < len(tokens) and tokens[i + 1]['type'] == 'ASSIGN':
                    if identifier not in self.symbol_table:
                        raise ValueError(
                            f"Variable '{identifier}' used before declaration")
                    if i + 2 < len(tokens) and tokens[i + 2]['type'] in ['NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE']:
                        value = tokens[i + 2]['value']
                        self.symbol_table[identifier]['value'] = value
                        i += 2
            i += 1

    def print_symbol_table(self):
        """Prints the symbol table in a formatted table."""
        print("Symbol Table:")
        print(
            f"{'Identifier':<20} {'Data Type':<10} {'Value':<15} {'Memory Location':<15}")
        print('-' * 70)
        for identifier, entry in self.symbol_table.items():
            value_display = '"' + \
                entry["value"] + \
                '"' if isinstance(entry["value"], str) else str(entry["value"])
            if entry["value"] is None:
                value_display = "None"
            print(
                f"{identifier:<20} {entry['data_type']:<10} {value_display:<15} {entry['memory_location']:<15}")
