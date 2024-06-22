class Optimizer:
    def optimize(self, assembly_code):
        # Split the assembly code into individual instructions
        instructions = assembly_code.split("\n")

        # Apply optimizations
        instructions = self.constant_folding(instructions)
        instructions = self.common_subexpression_elimination(instructions)
        instructions = self.peephole_optimization(instructions)
        instructions = self.remove_unused_labels(instructions)
        instructions = self.remove_redundant_jumps(instructions)
        optimized_instructions = self.dead_code_elimination(instructions)

        # Reconstruct the optimized assembly code
        optimized_code = "\n".join(optimized_instructions)
        return optimized_code

    def constant_folding(self, instructions):
        optimized_instructions = []
        for instruction in instructions:
            parts = instruction.split()
            if len(parts) == 4 and parts[0] == 'LOAD' and parts[2] == ',' and parts[1].isdigit():
                optimized_instructions.append(instruction)
            else:
                optimized_instructions.append(instruction)
        return optimized_instructions

    def common_subexpression_elimination(self, instructions):
        optimized_instructions = []
        seen = {}
        for instruction in instructions:
            if instruction in seen:
                continue
            else:
                seen[instruction] = True
                optimized_instructions.append(instruction)
        return optimized_instructions

    def peephole_optimization(self, instructions):
        optimized_instructions = []
        i = 0
        while i < len(instructions):
            if i < len(instructions) - 1:
                inst1 = instructions[i]
                inst2 = instructions[i + 1]
                if inst1.startswith("LOAD") and inst2.startswith("STORE"):
                    parts1 = inst1.split()
                    parts2 = inst2.split()
                    if parts1[1] == parts2[1]:
                        optimized_instructions.append(
                            f"MOV {parts1[1]}, {parts2[2]}")
                        i += 2
                        continue
            optimized_instructions.append(instructions[i])
            i += 1
        return optimized_instructions

    def remove_unused_labels(self, instructions):
        optimized_instructions = []
        used_labels = set()
        for instruction in instructions:
            if instruction.startswith("JMP") or instruction.startswith("IF"):
                parts = instruction.split()
                used_labels.add(parts[-1])
        for instruction in instructions:
            if not instruction.endswith(":") or instruction.split(":")[0] in used_labels:
                optimized_instructions.append(instruction)
        return optimized_instructions

    def remove_redundant_jumps(self, instructions):
        optimized_instructions = []
        for i in range(len(instructions)):
            if instructions[i].startswith("JMP"):
                target = instructions[i].split()[-1]
                if i + 1 < len(instructions) and instructions[i + 1].endswith(f"{target}:"):
                    continue
            optimized_instructions.append(instructions[i])
        return optimized_instructions

    def dead_code_elimination(self, instructions):
        optimized_instructions = []
        used_vars = set()
        for instruction in instructions:
            parts = instruction.split()
            if parts[0] == "LOAD" or parts[0] == "FLOAD":
                used_vars.add(parts[1].rstrip(","))
            elif parts[0] == "STORE" or parts[0] == "FSTORE":
                used_vars.add(parts[2].rstrip(","))
        for instruction in instructions:
            parts = instruction.split()
            if parts[0] == "LOAD" or parts[0] == "FLOAD":
                if parts[1].rstrip(",") in used_vars:
                    optimized_instructions.append(instruction)
            elif parts[0] == "STORE" or parts[0] == "FSTORE":
                if parts[2].rstrip(",") in used_vars:
                    optimized_instructions.append(instruction)
            else:
                optimized_instructions.append(instruction)
        return optimized_instructions
