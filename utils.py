def create_enhanced_symbol_table(tokens):
    """Creates a symbol table from tokens, useful for semantic analysis."""
    symbol_table = {}
    scope = "global"
    memory_location = 1000

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token['type'] == 'DATATYPE':
            if i + 1 < len(tokens) and tokens[i + 1]['type'] == 'VARIABLE':
                data_type = token['value']
                variable_name = tokens[i + 1]['value']
                i += 2
                value = None
                if i < len(tokens) and tokens[i]['type'] == 'ASSIGN':
                    i += 1
                    if i < len(tokens) and tokens[i]['type'] in ('NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE'):
                        value = tokens[i]['value']
                if variable_name not in symbol_table:
                    symbol_table[variable_name] = {
                        'Identifier': variable_name,
                        'Data Type': data_type,
                        'Value': value,
                        'Scope': scope,
                        'Memory Location': memory_location
                    }
                    memory_location += 4
        elif token['type'] == 'VARIABLE':
            # Handle variable assignments
            variable_name = token['value']
            if variable_name in symbol_table and i + 1 < len(tokens) and tokens[i + 1]['type'] == 'ASSIGN':
                i += 2
                if i < len(tokens) and tokens[i]['type'] in ('NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE'):
                    value = tokens[i]['value']
                    symbol_table[variable_name]['Value'] = value
        i += 1
    return symbol_table


# def print_symbol_table(symbol_table):
#     """ Prints the symbol table in a formatted table. """
#     print("Symbol Table:")
#     print(f"{'Identifier':<20} {'Data Type':<10} {'Value':<15} {'Scope':<10} {'Memory Location':<15}")
#     print('-' * 70)
#     for identifier, entry in symbol_table.items():
#         value_display = '"' + \
#             entry["Value"] + \
#             '"' if isinstance(entry["Value"], str) else str(entry["Value"])
#         if entry["Value"] is None:
#             value_display = "None"
#         print(f"{entry['Identifier']:<20} {entry['Data Type']:<10} {value_display:<15} {entry['Scope']:<10} {entry['Memory Location']:<15}")


def print_symbol_table(symbol_table):
    """ Formats the symbol table into a string. """
    output = "Symbol Table:\n"
    output += f"{'Identifier':<20} {'Data Type':<10} {'Value':<15} {'Scope':<10} {'Memory Location':<15}\n"
    output += '-' * 70 + '\n'
    for identifier, entry in symbol_table.items():
        value_display = f'"{entry["Value"]}"' if isinstance(
            entry["Value"], str) else str(entry["Value"])
        if entry["Value"] is None:
            value_display = "None"
        output += f"{entry['Identifier']:<20} {entry['Data Type']:<10} {value_display:<15} {entry['Scope']:<10} {entry['Memory Location']:<15}\n"
    return output
