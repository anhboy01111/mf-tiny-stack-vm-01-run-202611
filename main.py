# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Makefun Hunter Engine
# Stack-VM: Modular Bytecode Virtual Machine Engine (MIT License)

import sys
from typing import List, Dict, Any, Union, Optional

class OpCode:
    NOP   = 0x00
    PUSH  = 0x01  # PUSH <val>
    POP   = 0x02  # POP
    DUP   = 0x03  # DUP
    SWAP  = 0x04  # SWAP top two items
    ADD   = 0x10  # a + b
    SUB   = 0x11  # a - b
    MUL   = 0x12  # a * b
    DIV   = 0x13  # a / b
    MOD   = 0x14  # a % b
    NEG   = 0x15  # -a
    EQ    = 0x20  # a == b (1 or 0)
    NEQ   = 0x21  # a != b
    LT    = 0x22  # a < b
    GT    = 0x23  # a > b
    LE    = 0x24  # a <= b
    GE    = 0x25  # a >= b
    JMP   = 0x30  # JMP <addr>
    JZ    = 0x31  # JZ <addr> (jump if 0)
    JNZ   = 0x32  # JNZ <addr> (jump if not 0)
    CALL  = 0x40  # CALL <addr>
    RET   = 0x41  # RET
    LOAD  = 0x50  # LOAD <mem_addr>
    STORE = 0x51  # STORE <mem_addr>
    PRINT = 0x60  # PRINT top of stack
    HALT  = 0xFF  # Stop execution

class StackVM:
    """
    High-Performance Stack-based Virtual Machine.
    Zero network dependencies, pure algorithmic bytecode evaluation.
    """
    def __init__(self, memory_size: int = 1024, max_cycles: int = 100000):
        self.stack: List[Union[int, float, str]] = []
        self.call_stack: List[int] = []
        self.memory: List[Union[int, float, str]] = [0] * memory_size
        self.max_cycles = max_cycles
        self.output: List[str] = []
        self.pc = 0
        self.halted = False

    def load_program(self, bytecode: List[Any]):
        self.code = bytecode
        self.pc = 0
        self.stack.clear()
        self.call_stack.clear()
        self.output.clear()
        self.halted = False

    def run(self) -> Dict[str, Any]:
        cycles = 0
        code_len = len(self.code)

        while self.pc < code_len and not self.halted:
            cycles += 1
            if cycles > self.max_cycles:
                raise RuntimeError(f"VM cycle limit exceeded ({self.max_cycles})")

            op = self.code[self.pc]
            self.pc += 1

            if op == OpCode.NOP:
                continue

            elif op == OpCode.PUSH:
                val = self.code[self.pc]
                self.pc += 1
                self.stack.append(val)

            elif op == OpCode.POP:
                if self.stack:
                    self.stack.pop()

            elif op == OpCode.DUP:
                if self.stack:
                    self.stack.append(self.stack[-1])

            elif op == OpCode.SWAP:
                if len(self.stack) >= 2:
                    self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

            elif op == OpCode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)

            elif op == OpCode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif op == OpCode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif op == OpCode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a // b if isinstance(a, int) and isinstance(b, int) else a / b)

            elif op == OpCode.MOD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a % b)

            elif op == OpCode.NEG:
                self.stack[-1] = -self.stack[-1]

            elif op == OpCode.EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a == b else 0)

            elif op == OpCode.NEQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a != b else 0)

            elif op == OpCode.LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a < b else 0)

            elif op == OpCode.GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a > b else 0)

            elif op == OpCode.LE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a <= b else 0)

            elif op == OpCode.GE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a >= b else 0)

            elif op == OpCode.JMP:
                self.pc = int(self.code[self.pc])

            elif op == OpCode.JZ:
                target = int(self.code[self.pc])
                self.pc += 1
                cond = self.stack.pop()
                if cond == 0:
                    self.pc = target

            elif op == OpCode.JNZ:
                target = int(self.code[self.pc])
                self.pc += 1
                cond = self.stack.pop()
                if cond != 0:
                    self.pc = target

            elif op == OpCode.CALL:
                target = int(self.code[self.pc])
                self.pc += 1
                self.call_stack.append(self.pc)
                self.pc = target

            elif op == OpCode.RET:
                if not self.call_stack:
                    self.halted = True
                    break
                self.pc = self.call_stack.pop()

            elif op == OpCode.LOAD:
                addr = int(self.code[self.pc])
                self.pc += 1
                self.stack.append(self.memory[addr])

            elif op == OpCode.STORE:
                addr = int(self.code[self.pc])
                self.pc += 1
                val = self.stack.pop()
                self.memory[addr] = val

            elif op == OpCode.PRINT:
                val = self.stack.pop() if self.stack else ""
                self.output.append(str(val))

            elif op == OpCode.HALT:
                self.halted = True
                break

            else:
                raise ValueError(f"Unknown OpCode: {op}")

        return {
            "cycles": cycles,
            "top": self.stack[-1] if self.stack else None,
            "stack": list(self.stack),
            "output": list(self.output)
        }

def assemble(asm_text: str) -> List[Any]:
    """Compile simple assembly text into bytecode with label resolution."""
    lines = [line.split(';')[0].strip() for line in asm_text.splitlines()]
    labels = {}
    tokens = []
    
    # First pass: collect labels and rough token positions
    pos = 0
    raw_ops = []
    for line in lines:
        if not line:
            continue
        if line.endswith(':'):
            labels[line[:-1].strip()] = pos
        else:
            parts = line.split()
            op_name = parts[0].upper()
            args = parts[1:]
            raw_ops.append((op_name, args))
            pos += 1 + len(args)

    # Second pass: encode bytecode
    bytecode = []
    for op_name, args in raw_ops:
        op = getattr(OpCode, op_name, None)
        if op is None:
            raise ValueError(f"Invalid instruction '{op_name}'")
        bytecode.append(op)
        for arg in args:
            if arg in labels:
                bytecode.append(labels[arg])
            elif arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
                bytecode.append(int(arg))
            else:
                try:
                    bytecode.append(float(arg))
                except ValueError:
                    bytecode.append(arg)

    return bytecode

if __name__ == "__main__":
    # Self-test: Calculate 10th Fibonacci number
    asm = """
    PUSH 0      ; mem[0] = a = 0
    STORE 0
    PUSH 1      ; mem[1] = b = 1
    STORE 1
    PUSH 10     ; mem[2] = count = 10
    STORE 2

loop:
    LOAD 2
    JZ done     ; if count == 0 goto done
    LOAD 0
    LOAD 1
    ADD         ; c = a + b
    LOAD 1
    STORE 0     ; a = b
    STORE 1     ; b = c
    LOAD 2
    PUSH 1
    SUB
    STORE 2     ; count--
    JMP loop

done:
    LOAD 0
    PRINT
    HALT
    """
    vm = StackVM()
    code = assemble(asm)
    vm.load_program(code)
    result = vm.run()
    print("StackVM Execution Result:", result)
