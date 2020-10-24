from dataclasses import dataclass
from typing import Optional, Dict, Union


def bin_without_prefix(n: int, bits: int) -> str:
    b = bin(n)[2:]  # strip leading `0b`
    padding = "0" * (bits - len(b))
    return padding + b


class SymbolTable:
    def __init__(self):
        self.last_variable_address = 0x000F
        self.label2address: Dict[str, int] = {
            "SP": 0x0000,
            "LCL": 0x0001,
            "ARG": 0x0002,
            "THIS": 0x0003,
            "THAT": 0x0004,
            "R0": 0x0000,
            "R1": 0x0001,
            "R2": 0x0002,
            "R3": 0x0003,
            "R4": 0x0004,
            "R5": 0x0005,
            "R6": 0x0006,
            "R7": 0x0007,
            "R8": 0x0008,
            "R9": 0x0009,
            "R10": 0x000A,
            "R11": 0x000B,
            "R12": 0x000C,
            "R13": 0x000D,
            "R14": 0x000E,
            "R15": 0x000F,
            "SCREEN": 0x4000,
            "KBD": 0x6000,
        }

    def add(self, label: str, address: int) -> None:
        self.label2address[label] = address

    def get(self, label: str) -> Optional[int]:
        return self.label2address.get(label)

    def create_variable(self) -> int:
        self.last_variable_address += 1
        return self.last_variable_address


class AssemblyCommand:
    @staticmethod
    def from_line(line: str) -> "AssemblyCommand":
        raise NotImplementedError("Should be implemented by a subclass")


@dataclass(frozen=True)
class AInstruction(AssemblyCommand):
    value_xor_label: Union[int, str]

    @staticmethod
    def from_line(line: str) -> "AInstruction":
        if line[1].isdigit():
            arg = int(line[1:])
        else:
            arg = line[1:]
        return AInstruction(arg)

    def gen_code(self, symbol_table: SymbolTable) -> str:
        if isinstance(self.value_xor_label, int):
            result = bin_without_prefix(self.value_xor_label, 16)
        if isinstance(self.value_xor_label, str):
            address = symbol_table.get(self.value_xor_label)
            if address is None:
                # create a new variable
                address = symbol_table.create_variable()
                symbol_table.add(self.value_xor_label, address)
            result = bin_without_prefix(address, 16)
        assert len(result) == 16
        return result


@dataclass(frozen=True)
class CInstruction(AssemblyCommand):
    comp: str
    dest: Optional[str] = None
    jump: Optional[str] = None

    """
    dest=comp;jump
    dest=comp
    comp;jump
    
    Either the `dest` or `jump` fields may be empty.
    If `dest` is empty, the `=` is omitted.
    If `jump` is empty, the `;` is omitted.
    """

    @staticmethod
    def from_line(line: str) -> "CInstruction":
        if "=" in line:
            left, right = line.split("=", 1)
            return CInstruction(dest=left, comp=right)
        left, jump = line.split(";", 1)
        return CInstruction(comp=left, jump=jump)

    def _gen_code_dest(self, dest: str) -> str:
        dests = [None, "M", "D", "MD", "A", "AM", "AD", "AMD"]
        result = bin_without_prefix(dests.index(dest), 3)
        assert len(result) == 3
        return result

    def _gen_code_jump(self, jump: str) -> str:
        jumps = [None, "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]
        result = bin_without_prefix(jumps.index(jump), 3)
        assert len(result) == 3
        return result

    def _gen_code_comp(self, comp: str) -> str:
        comp2bin = {
            # with a=0
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            # with a=1
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101",
        }
        result = comp2bin[comp]
        assert len(result) == 7
        return result

    def gen_code(self) -> str:
        result = (
            "111"
            + self._gen_code_comp(self.comp)
            + self._gen_code_dest(self.dest)
            + self._gen_code_jump(self.jump)
        )
        assert len(result) == 16
        return result


@dataclass(frozen=True)
class Label(AssemblyCommand):
    label: str

    @staticmethod
    def from_line(line: str) -> "Label":
        label = line[1:-1]  # strip `"("` and `")"` from `"(LABEL)"`
        return Label(label)


class Assembler:
    @staticmethod
    def strip_comment(line: str) -> str:
        try:
            index = line.index("//")
        except ValueError:
            return line  # no comment found
        return line[:index]

    @classmethod
    def parse_line(cls, line: str) -> Optional[AssemblyCommand]:
        line = cls.strip_comment(line).strip().replace(" ", "")
        if not line:
            return
        # Now `line` must be one of: A-instruction, C-instruction or a label
        if line.startswith("@"):
            return AInstruction.from_line(line)
        if line.startswith("("):
            return Label.from_line(line)
        else:
            return CInstruction.from_line(line)


def main() -> None:
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: ./main.py SOURCE.asm")
        sys.exit(1)
    path = sys.argv[1]
    commands = []
    symbol_table = SymbolTable()
    next_instruction_address = 0x0000
    with open(path, "r") as f:
        for line in f:
            command = Assembler.parse_line(line)
            if command:
                if isinstance(command, Label):
                    symbol_table.add(command.label, next_instruction_address)
                else:
                    commands.append(command)
                    next_instruction_address += 1
    with open(path[:-3] + "hack", "w") as f:
        for command in commands:
            if isinstance(command, AInstruction):
                f.write(command.gen_code(symbol_table))
                f.write("\n")
            elif isinstance(command, CInstruction):
                f.write(command.gen_code())
                f.write("\n")
            else:
                raise NotImplementedError("should never happen")


if __name__ == "__main__":
    main()
