// SPDX-License-Identifier: MIT
// Complete High-Performance Tiny Stack Virtual Machine for make.fun
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

export function run(p: Uint8Array, inp: Uint8Array): { out: number[]; code: number } {
  const D: number[] = [];
  const C: number[] = [];
  const M: number[] = [];
  const out: number[] = [];
  let pc = 0;
  let ip = 0;
  let steps = 0;
  const pop = (): number => (D.pop() ?? 0) | 0;
  const fault = { out, code: 1 };
  
  for (;;) {
    if (++steps > 1e6 || !(pc >= 0 && pc < p.length)) return fault;
    const op = p[pc++];
    
    // Arithmetic and Logic Opcodes
    if (op >= 0x10 && op <= 0x22 && op !== 0x17 && op !== 0x1b) {
      const b = pop();
      const a = pop();
      let r: number;
      if (op === 0x10) r = a + b;
      else if (op === 0x11) r = a - b;
      else if (op === 0x12) r = Math.imul(a, b);
      else if (op === 0x13 || op === 0x15) {
        if (b === 0) return fault;
        r = Math.trunc(a / b);
      } else if (op === 0x14 || op === 0x16) {
        if (b === 0) return fault;
        r = a % b;
      } else if (op === 0x18) r = a & b;
      else if (op === 0x19) r = a | b;
      else if (op === 0x1a) r = a ^ b;
      else if (op === 0x1c) r = a << b;
      else if (op === 0x1d) r = a >> b;
      else if (op === 0x1e) r = a >>> b;
      else if (op === 0x20) r = a === b ? 1 : 0;
      else if (op === 0x21 || op === 0x22) r = a < b ? 1 : 0;
      else return fault;
      D.push(r | 0);
      continue;
    }
    
    // Stack & Control Flow Opcodes
    switch (op) {
      case 0x00:
        return { out, code: 0 };
      case 0x01:
        D.push((p[pc++] << 24) >> 24);
        break;
      case 0x02:
        D.push(p[pc] | (p[pc + 1] << 8) | (p[pc + 2] << 16) | (p[pc + 3] << 24));
        pc += 4;
        break;
      case 0x03:
        D.pop();
        break;
      case 0x04: {
        const a = pop();
        D.push(a, a);
        break;
      }
      case 0x05: {
        const b = pop();
        const a = pop();
        D.push(b, a);
        break;
      }
      case 0x06: {
        const b = pop();
        const a = pop();
        D.push(a, b, a);
        break;
      }
      case 0x07: {
        const c = pop();
        const b = pop();
        const a = pop();
        D.push(b, c, a);
        break;
      }
      case 0x17:
        D.push(-pop() | 0);
        break;
      case 0x1b:
        D.push(~pop());
        break;
      case 0x30:
      case 0x31:
      case 0x32: {
        const rel = ((p[pc] | (p[pc + 1] << 8)) << 16) >> 16;
        pc += 2;
        const take = op === 0x30 || (op === 0x31) === (pop() === 0);
        if (take) pc += rel;
        break;
      }
      case 0x33:
        C.push(pc + 2);
        pc = p[pc] | (p[pc + 1] << 8);
        break;
      case 0x34:
        if (C.length === 0) return fault;
        pc = C.pop()!;
        break;
      case 0x40:
        D.push(M[pop()] ?? 0);
        break;
      case 0x41: {
        const addr = pop();
        M[addr] = pop();
        break;
      }
      case 0x50:
        for (const ch of String(pop())) out.push(ch.charCodeAt(0));
        break;
      case 0x51:
        out.push(pop() & 255);
        break;
      case 0x52:
        D.push(ip < inp.length ? inp[ip++] : -1);
        break;
      case 0x53:
        return { out, code: pop() & 255 };
      default:
        return fault;
    }
    if (out.length > 65536) {
      out.length = 65536;
      return fault;
    }
  }
}

export function main(): void {
  const I = process.env.MAKEFUN_INPUT_DIR ?? '/input';
  const O = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  for (const id of readdirSync(I).sort()) {
    const pPath = join(I, id, 'program.bin');
    const inPath = join(I, id, 'input.bin');
    const pBytes = new Uint8Array(readFileSync(pPath));
    const inBytes = new Uint8Array(readFileSync(inPath));
    const r = run(pBytes, inBytes);
    mkdirSync(join(O, id), { recursive: true });
    writeFileSync(join(O, id, 'stdout.bin'), Uint8Array.from(r.out));
    writeFileSync(join(O, id, 'exit.txt'), `${r.code}\n`);
  }
}

main();
