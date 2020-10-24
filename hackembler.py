from dataclasses import dataclass
from typing import Optional


def bin_without_prefix(n: int, bits: int) -> str:
    b = bin(n)[2:]  # strip leading `0b`
    padding = "0" * (bits - len(b))
    return padding + b


class AssemblyCommand:
    @staticmethod
    def from_line(line: str) -> "AssemblyCommand":
        raise NotImplementedError("Should be implemented by a subclass")


@dataclass(frozen=True)
class AInstruction(AssemblyCommand):
    value: int

    @staticmethod
    def from_line(line: str) -> "AInstruction":
        return AInstruction(int(line[1:]))

    def gen_code(self) -> str:
        result = bin_without_prefix(self.value, 16)
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
    @staticmethod
    def from_line(line: str) -> "Label":
        raise NotImplementedError("todo")


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
    with open(path, "r") as f:
        for line in f:
            command = Assembler.parse_line(line)
            if command:
                if isinstance(command, (AInstruction, CInstruction)):
                    print(command.gen_code())


if __name__ == "__main__":
    main()
