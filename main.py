from tokenizer import tokenize
from Parser import Parser, SyntaxError
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from utils import create_enhanced_symbol_table, print_symbol_table

if __name__ == '__main__':
    source_code = '''
    enum v-age = 18,
    efl v-pi = 3.14,
    estr v-name = "Alice",
    ebool v-enrolled = yup,
    estr v-message,
    iff (v-age >= 18) {
         v-message = "Eligible to vote",
    } maybe (v-age < 18) {
         v-message = "Hello youngster",
    } orelse {
         v-message = "Welcome, age not specified",
    }

    // Printing PI value
    estr v-piString = "The value of PI is: ",
    efl v-displayPi = v-pi,

    //whilst loop
    enum v-count = 0, 
    whilst (v-age < 10) {
        v-count = v-count + 1,
    }
    '''

    tokens, errors = tokenize(source_code)  # Tokenization
    for token in tokens:
        print(token)
    if errors:  # Check if there are any errors
        print("\nErrors detected:")
        for error in errors:
            print(error)

    if not errors:
        parser = Parser(tokens, source_code)
        try:
            parser.parse()
            print("Parsing completed successfully.")
        except SyntaxError as e:
            print(f"Syntax error: {e}")
    else:
        print("Errors in source code:")
        for error in errors:
            print(error)

    if not errors:
        symbol_table = create_enhanced_symbol_table(tokens)
        print_symbol_table(symbol_table)
    else:
        print("Errors in source code, cannot create a valid symbol table:")
        for error in errors:
            print(error)

    if not errors:
        semantic_analyzer = SemanticAnalyzer()
        try:
            semantic_analyzer.analyze_code(tokens)
            print("Semantic analysis successful!")
            print("Symbol Table:")
            for var_name, var_info in semantic_analyzer.symbol_table.items():
                print(f"{var_name}: {var_info}")

            # Generate assembly code
            code_generator = CodeGenerator()
            code_generator.set_symbol_table(symbol_table)
            assembly_code = code_generator.generate_code(tokens)
            print("\nGenerated Assembly Code:")
            print(assembly_code)

        except ValueError as e:
            print(f"Semantic error: {e}")
    else:
        print("Errors in source code, cannot perform semantic analysis.")
