class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.symbol_table = {}
        self.memory_location_counter = 1000
        self.output = None
        self.inputs = {}  # Dictionary to store input values

    def set_symbol_table(self, symbol_table):
        self.symbol_table = symbol_table

    def generate_code(self, tokens):
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token['type'] == 'DATATYPE':
                data_type = token['value']
                if i + 1 < len(tokens) and tokens[i + 1]['type'] == 'VARIABLE':
                    identifier = tokens[i + 1]['value']
                    value = None
                    if i + 2 < len(tokens) and tokens[i + 2]['type'] == 'ASSIGN':
                        if i + 3 < len(tokens) and tokens[i + 3]['type'] in ['NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE']:
                            value = tokens[i + 3]['value']
                            i += 3
                        else:
                            i += 2
                    else:
                        i += 1
                    self._generate_variable_code(identifier, data_type, value)
            elif token['type'] == 'VARIABLE':
                identifier = token['value']
                if i + 1 < len(tokens) and tokens[i + 1]['type'] == 'ASSIGN':
                    if i + 2 < len(tokens) and tokens[i + 2]['type'] in ['NUMBER', 'STRING', 'BOOLEAN_VAL', 'VARIABLE']:
                        value = tokens[i + 2]['value']
                        self._generate_assignment_code(identifier, value)
                        i += 2
            elif token['type'] in ['IFF', 'MAYBE', 'ORELSE']:
                self._generate_conditional_code(tokens, i)
            elif token['type'] == 'WHILST':
                self._generate_whilst_code(tokens, i)
            elif token['type'] == 'OPERATOR':
                if token['value'] == '+':
                    self._generate_addition_code(tokens, i)
                    i += 1
                # Add more operators as needed
            i += 1
        return "\n".join(self.instructions)

    def _generate_variable_code(self, identifier, data_type, value):
        memory_location = self.memory_location_counter
        self.memory_location_counter += 4
        self.symbol_table[identifier] = {
            'data_type': data_type, 'memory_location': memory_location}

        if data_type == 'enum':
            if value is not None:
                self.instructions.append(
                    f"LOAD {value}, r1")
                self.instructions.append(
                    f"STORE r1, {memory_location}")
        elif data_type == 'efl':
            if value is not None:
                self.instructions.append(
                    f"FLOAD {value}, fr1")
                self.instructions.append(
                    f"FSTORE fr1, {memory_location}")
        elif data_type == 'estr':
            if value is not None:
                self.instructions.append(
                    f'STR "{value}", {memory_location}')
        elif data_type == 'ebool':
            boolean_value = 1 if value == 'yup' else 0
            self.instructions.append(
                f"LOAD {boolean_value}, r1")
            self.instructions.append(
                f"STORE r1, {memory_location}")

    def _generate_assignment_code(self, identifier, value):
        if identifier in self.symbol_table:
            memory_location = self.symbol_table[identifier]['memory_location']
            data_type = self.symbol_table[identifier]['data_type']
            if data_type == 'enum':
                if value.isdigit():
                    self.instructions.append(
                        f"LOAD {value}, r1")
                else:
                    mem_loc = self.symbol_table[value]['memory_location']
                    self.instructions.append(
                        f"LOAD {mem_loc}, r1")
                self.instructions.append(
                    f"STORE r1, {memory_location}")
            elif data_type == 'efl':
                if self._is_float(value):
                    self.instructions.append(
                        f"FLOAD {value}, fr1")
                else:
                    mem_loc = self.symbol_table[value]['memory_location']
                    self.instructions.append(
                        f"FLOAD {mem_loc}, fr1")
                self.instructions.append(
                    f"FSTORE fr1, {memory_location}")
            elif data_type == 'estr':
                self.instructions.append(
                    f'STR "{value}", {memory_location}')
            elif data_type == 'ebool':
                boolean_value = 1 if value == 'yup' else 0
                self.instructions.append(
                    f"LOAD {boolean_value}, r1")
                self.instructions.append(
                    f"STORE r1, {memory_location}")

    def _is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _generate_conditional_code(self, tokens, i):
        condition_start = tokens[i]['value']
        condition_code = []
        i += 1  # Skip 'IFF', 'MAYBE', 'ORELSE'
        if tokens[i]['type'] == 'LPAREN':
            i += 1  # Skip '('
            while tokens[i]['type'] != 'RPAREN':
                condition_code.append(tokens[i])
                i += 1
            i += 1  # Skip ')'
        self.instructions.append(f"; Begin {condition_start} condition")
        self._generate_condition(condition_code)
        self.instructions.append(f"; End {condition_start} condition")

    def _generate_condition(self, condition_code):
        condition = " ".join([token['value'] for token in condition_code])
        self.instructions.append(f"IF {condition} THEN")

    def _generate_whilst_code(self, tokens, i):
        self.instructions.append("; Begin WHILST loop")
        i += 1  # Skip 'WHILST'
        if tokens[i]['type'] == 'LPAREN':
            i += 1  # Skip '('
            condition_code = []
            while tokens[i]['type'] != 'RPAREN':
                condition_code.append(tokens[i])
                i += 1
            i += 1  # Skip ')'
            self._generate_condition(condition_code)
            self.instructions.append("; WHILST body")
            if tokens[i]['type'] == 'LCURLY':
                i += 1  # Skip '{'
                while tokens[i]['type'] != 'RCURLY':
                    if tokens[i]['type'] == 'VARIABLE' and tokens[i + 1]['type'] == 'ASSIGN':
                        self._generate_assignment_code(
                            tokens[i]['value'], tokens[i + 2]['value'])
                        i += 2
                    i += 1
                self.instructions.append("; End WHILST body")
        self.instructions.append("; End WHILST loop")

    def _generate_addition_code(self, tokens, i):
        operand1 = tokens[i - 1]['value']
        operand2 = tokens[i + 1]['value']
        if operand1.isdigit() and operand2.isdigit():
            result = int(operand1) + int(operand2)
            self.output = result
            self.instructions.append(f"LOAD {operand1}, r1")
            self.instructions.append(f"ADD {operand2}, r1, r2")
            self.instructions.append(
                f"STORE r2, {self.memory_location_counter}")
            self.memory_location_counter += 4
        else:
            if operand1 in self.symbol_table:
                self.instructions.append(
                    f"LOAD {self.symbol_table[operand1]['memory_location']}, r1")
            else:
                self.instructions.append(f"LOAD {operand1}, r1")
            if operand2 in self.symbol_table:
                self.instructions.append(
                    f"LOAD {self.symbol_table[operand2]['memory_location']}, r2")
            else:
                self.instructions.append(f"LOAD {operand2}, r2")
            self.instructions.append(f"ADD r2, r1, r3")
            self.instructions.append(
                f"STORE r3, {self.memory_location_counter}")
            self.memory_location_counter += 4

        # Set the output to the result of the addition
        self.output = result

    def execute_code(self):
        if self.output is not None:
            print(self.output)
        else:
            print("No output to display.")

    def _read_input(self, identifier):
        if identifier in self.inputs:
            value = self.inputs[identifier]
            return value
        else:
            return None

    def set_inputs(self, inputs):
        self.inputs = inputs
