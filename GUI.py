import tkinter as tk
from tkinter import scrolledtext, filedialog
from tkinter import ttk
import re
from tokenizer import tokenize
from Parser import Parser, SyntaxError
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from utils import create_enhanced_symbol_table, print_symbol_table


class CompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compiler GUI")
        self.geometry("1920x1080")
        self.configure(bg='#1e1e1e')  # Dark background

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#1e1e1e',
                             foreground='#d4d4d4', font=('Consolas', 12))
        self.style.configure('TButton', background='#007acc',
                             foreground='#ffffff', font=('Consolas', 12))
        self.style.configure('TFrame', background='#1e1e1e')
        self.style.configure(
            'TNotebook', background='#1e1e1e', foreground='#d4d4d4')
        self.style.configure('TNotebook.Tab', background='#252526',
                             foreground='#d4d4d4', font=('Consolas', 10))

        # Create widgets
        self.create_widgets()

        # Add syntax highlighting
        self.syntax_highlight()

    def create_widgets(self):
        # Title frame
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X)

        # Title label
        title_label = ttk.Label(title_frame, text="Enigma Language Compiler",
                                style='TLabel', font=('Consolas', 24, 'bold'))
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        # Open button
        self.open_button = ttk.Button(
            title_frame, text="Open File", command=self.open_file, style='TButton')
        self.open_button.pack(side=tk.LEFT, padx=(20, 10), pady=20)

        # Save button
        self.save_button = ttk.Button(
            title_frame, text="Save File", command=self.save_file, style='TButton')
        self.save_button.pack(side=tk.LEFT, pady=20)

        # Create a frame for the code input and output
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Line number area
        line_number_frame = ttk.Frame(frame, width=30)
        line_number_frame.pack(fill=tk.Y, side=tk.LEFT, pady=30)

        self.line_number_text = scrolledtext.ScrolledText(
            line_number_frame, width=2, wrap=tk.NONE, bg='#1e1e1e', fg='#d4d4d4', insertbackground='#d4d4d4', state="disabled")
        self.line_number_text.pack(fill=tk.Y, expand=True)

        # Source code input area
        code_frame = ttk.Frame(frame)
        code_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(10, 0))

        self.code_label = ttk.Label(
            code_frame, text="Source Code:", style='TLabel', font=('Consolas', 14))
        self.code_label.pack(anchor='w', pady=(0, 5))

        self.code_text = scrolledtext.ScrolledText(
            code_frame, width=80, wrap=tk.WORD, font=('Consolas', 12), bg='#252526', fg='#d4d4d4', insertbackground='#d4d4d4')
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.bind("<KeyRelease>", self.syntax_highlight)
        self.code_text.bind("<Control-z>", self.undo)
        self.code_text.bind("<Control-y>", self.redo)

        # Configure scrollbar for code_text and line_number_text synchronization
        self.scrollbar = ttk.Scrollbar(
            code_frame, orient=tk.VERTICAL, command=self.scroll_text)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.config(yscrollcommand=self.scrollbar.set)
        self.line_number_text.config(yscrollcommand=self.scrollbar.set)

        # Bind scrolling to synchronize line numbers with code_text
        self.code_text.bind('<Configure>', self.update_line_numbers)
        self.code_text.bind('<FocusIn>', self.update_line_numbers)
        self.code_text.bind('<FocusOut>', self.update_line_numbers)
        self.code_text.bind('<MouseWheel>', self.on_mousewheel)

        # Button Frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=10, pady=40)

        self.run_button = ttk.Button(
            button_frame, text="Run Compiler", command=self.run_compiler, style='TButton')
        self.run_button.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.show_tokens_button = ttk.Button(
            button_frame, text="Show Tokens", command=self.show_tokens, style='TButton')
        self.show_tokens_button.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.show_symbol_table_button = ttk.Button(
            button_frame, text="Show Symbol Table", command=self.show_symbol_table, style='TButton')
        self.show_symbol_table_button.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.run_code_generator_button = ttk.Button(
            button_frame, text="Run Code Generator", command=self.run_code_generator, style='TButton')
        self.run_code_generator_button.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.show_output_button = ttk.Button(
            button_frame, text="Show Output", command=self.show_output, style='TButton')
        self.show_output_button.pack(fill=tk.X, pady=(0, 10), padx=5)

        ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=5, pady=(500, 5))  # Separator for spacing

        # Exit and Clear buttons
        self.exit_button = ttk.Button(
            button_frame, text="Exit", command=self.quit, style='TButton')
        self.exit_button.pack(side=tk.RIGHT, padx=5, pady=(20, 10))

        self.clear_button = ttk.Button(
            button_frame, text="Clear", command=self.clear_text, style='TButton')
        self.clear_button.pack(side=tk.RIGHT, padx=5, pady=(20, 10))

        # Errors and output
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill=tk.BOTH, expand=True,
                          side=tk.LEFT, padx=10, pady=10)

        self.errors_label = ttk.Label(
            output_frame, text="Errors:", style='TLabel', font=('Consolas', 14))
        self.errors_label.pack(anchor='w', pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            output_frame, width=80, height=10, wrap=tk.WORD, font=('Consolas', 12), bg='#252526', fg='#d4d4d4', insertbackground='#d4d4d4', state="disabled")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Initialize line numbers
        self.update_line_numbers()

        # Store generated assembly code
        self.generated_assembly_code = None

    def update_line_numbers(self, event=None):
        # Update line numbers based on current content in code_text
        lines = self.code_text.get("1.0", tk.END).count('\n') + 1
        line_numbers = '\n'.join(str(i) for i in range(1, lines))
        self.line_number_text.config(state=tk.NORMAL)
        self.line_number_text.delete(1.0, tk.END)
        self.line_number_text.insert(tk.END, line_numbers)
        self.line_number_text.config(state=tk.DISABLED)

    def scroll_text(self, *args):
        self.code_text.yview(*args)
        self.line_number_text.yview(*args)

    def on_mousewheel(self, event):
        self.code_text.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_number_text.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(tk.END, content)
            self.syntax_highlight()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[
                                                 ("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                content = self.code_text.get(1.0, tk.END)
                file.write(content)

    def show_tokens(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        try:
            tokens = tokenize(self.code_text.get(1.0, tk.END))
            token_str = "\n".join([str(token) for token in tokens])
            self.output_text.insert(tk.END, token_str)
        except SyntaxError as e:
            self.output_text.insert(tk.END, f"SyntaxError: {str(e)}\n")
        self.output_text.config(state=tk.DISABLED)

    def show_symbol_table(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        try:
            tokens = tokenize(self.code_text.get(1.0, tk.END))
            parser = Parser(tokens)
            program = parser.parse()
            semantic_analyzer = SemanticAnalyzer()
            semantic_analyzer.visit(program)
            symbol_table_str = print_symbol_table(
                create_enhanced_symbol_table(program))
            self.output_text.insert(tk.END, symbol_table_str)
        except SyntaxError as e:
            self.output_text.insert(tk.END, f"SyntaxError: {str(e)}\n")
        self.output_text.config(state=tk.DISABLED)

    def run_code_generator(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        source_code = self.code_text.get(1.0, tk.END)
        tokens, errors = tokenize(source_code)
        if not errors:
            parser = Parser(tokens, source_code)
            try:
                parser.parse()
                symbol_table = create_enhanced_symbol_table(tokens)
                semantic_analyzer = SemanticAnalyzer()
                semantic_analyzer.analyze_code(tokens)
                code_generator = CodeGenerator()
                code_generator.set_symbol_table(symbol_table)
                assembly_code = code_generator.generate_code(tokens)
                self.generated_assembly_code = assembly_code  # Store the generated code
                self.output_text.insert(tk.END, "Generated Assembly Code:\n\n")
                self.output_text.insert(tk.END, f"{assembly_code}\n")

                # Execute the code to get the output
                output = execute_assembly_code(assembly_code)
                self.output_text.insert(tk.END, "\nOutput:\n\n")
                self.output_text.insert(tk.END, f"{output}\n")

            except SyntaxError as e:
                self.output_text.insert(tk.END, f"Syntax error: {e}\n")
            except ValueError as e:
                self.output_text.insert(tk.END, f"Semantic error: {e}\n")
        else:
            self.output_text.insert(
                tk.END, "Errors in source code, cannot generate code:\n")
            for error in errors:
                self.output_text.insert(tk.END, f"{error}\n")
        self.output_text.config(state=tk.DISABLED)

    def show_symbol_table(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        source_code = self.code_text.get(1.0, tk.END)
        tokens, errors = tokenize(source_code)
        if not errors:
            symbol_table = create_enhanced_symbol_table(tokens)
            output = print_symbol_table(symbol_table)
            self.output_text.insert(tk.END, output)  # Insert formatted output
        else:
            self.output_text.insert(
                tk.END, "Errors in source code, cannot create a valid symbol table:\n")
            for error in errors:
                self.output_text.insert(tk.END, f"{error}\n")
        self.output_text.config(state=tk.DISABLED)

    def show_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        if self.generated_assembly_code:
            output = execute_assembly_code(self.generated_assembly_code)
            self.output_text.insert(tk.END, "Output:\n\n")
            self.output_text.insert(tk.END, f"{output}\n")
        else:
            self.output_text.insert(
                tk.END, "No generated assembly code to execute.\n")
        self.output_text.config(state=tk.DISABLED)

    def run_compiler(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        source_code = self.code_text.get(1.0, tk.END)

        # Tokenize source code
        tokens, errors = tokenize(source_code)

        if errors:
            self.output_text.insert(tk.END, "Errors in source code:\n")
            for error in errors:
                self.output_text.insert(tk.END, f"{error}\n")
        else:
            # Parsing phase
            parser = Parser(tokens, source_code)
            try:
                parser.parse()
                self.output_text.insert(
                    tk.END, "Parsing completed successfully.\n")

                # Semantic analysis phase
                semantic_analyzer = SemanticAnalyzer()
                try:
                    semantic_analyzer.analyze_code(tokens)
                    self.output_text.insert(
                        tk.END, "Semantic analysis completed successfully.\n")

                    # Code generation phase
                    symbol_table = create_enhanced_symbol_table(tokens)
                    code_generator = CodeGenerator()
                    code_generator.set_symbol_table(symbol_table)
                    assembly_code = code_generator.generate_code(tokens)
                    self.generated_assembly_code = assembly_code  # Store the generated code
                    self.output_text.insert(
                        tk.END, "Code generation completed successfully.\n")
                    self.output_text.insert(
                        tk.END, "Generated Assembly Code:\n\n")
                    self.output_text.insert(tk.END, f"{assembly_code}\n")

                    # Execute the code to get the output
                    output = execute_assembly_code(assembly_code)
                    self.output_text.insert(tk.END, "\nOutput:\n\n")
                    self.output_text.insert(tk.END, f"{output}\n")

                except ValueError as e:
                    # Handle semantic errors
                    self.output_text.insert(
                        tk.END, f"Semantic error: {str(e)}\n")
                    self.output_text.insert(
                        tk.END, "Please correct the semantic error and try again.\n")

            except SyntaxError as e:
                # Handle syntax errors
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Syntax error: {str(e)}\n")
                self.output_text.insert(
                    tk.END, "Please correct the syntax error and try again.\n")

        # Disable text editing
        self.output_text.config(state=tk.DISABLED)

    def clear_text(self):
        self.code_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def undo(self, event=None):
        self.code_text.edit_undo()
        return "break"

    def redo(self, event=None):
        self.code_text.edit_redo()
        return "break"

    def syntax_highlight(self, event=None):
        # Remove previous tags
        self.code_text.tag_remove("keyword", "1.0", tk.END)
        self.code_text.tag_remove("comment", "1.0", tk.END)
        self.code_text.tag_remove("string", "1.0", tk.END)
        self.code_text.tag_remove("number", "1.0", tk.END)
        self.code_text.tag_remove("identifier", "1.0", tk.END)

        # Define the tag configurations for syntax highlighting
        self.code_text.tag_configure("keyword", foreground="#569cd6")
        self.code_text.tag_configure("comment", foreground="#6a9955")
        self.code_text.tag_configure("string", foreground="#d69d85")
        self.code_text.tag_configure("number", foreground="#b5cea8")
        self.code_text.tag_configure("identifier", foreground="#9cdcfe")

        keywords = ["if", "else", "for", "while",
                    "return", "function", "var", "const", "let"]
        keyword_pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b')
        comment_pattern = re.compile(r'//.*|/\*[\s\S]*?\*/')
        string_pattern = re.compile(r'".*?"')
        number_pattern = re.compile(r'\b\d+\b')
        identifier_pattern = re.compile(r'\b[A-Za-z_]\w*\b')

        content = self.code_text.get("1.0", tk.END)
        for match in keyword_pattern.finditer(content):
            start, end = match.span()
            self.code_text.tag_add("keyword", f"1.0+{start}c", f"1.0+{end}c")
        for match in comment_pattern.finditer(content):
            start, end = match.span()
            self.code_text.tag_add("comment", f"1.0+{start}c", f"1.0+{end}c")
        for match in string_pattern.finditer(content):
            start, end = match.span()
            self.code_text.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")
        for match in number_pattern.finditer(content):
            start, end = match.span()
            self.code_text.tag_add("number", f"1.0+{start}c", f"1.0+{end}c")
        for match in identifier_pattern.finditer(content):
            if match.group(0) not in keywords:
                start, end = match.span()
                self.code_text.tag_add(
                    "identifier", f"1.0+{start}c", f"1.0+{end}c")


def execute_assembly_code(assembly_code):
    # Simulate executing the generated assembly code
    # This function should interpret the generated assembly code
    # For the purpose of this example, we will handle simple instructions like LOAD, STORE, ADD
    memory = {}
    registers = {'r1': 0, 'r2': 0}

    lines = assembly_code.splitlines()

    for line in lines:
        parts = line.split()
        instruction = parts[0]

        if instruction == "LOAD":
            value = int(parts[1].strip(','))
            register = parts[2]
            registers[register] = value
        elif instruction == "STORE":
            register = parts[1].strip(',')
            address = int(parts[2])
            memory[address] = registers[register]
        elif instruction == "ADD":
            value = int(parts[1].strip(','))
            src_register = parts[2].strip(',')
            dest_register = parts[3]
            registers[dest_register] = registers[src_register] + value

    # Generate output
    output = "\n".join(
        f"Memory[{address}] = {value}" for address, value in sorted(memory.items()))
    return output


if __name__ == "__main__":
    app = CompilerGUI()
    app.mainloop()
