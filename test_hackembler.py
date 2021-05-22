from hackembler import CInstruction, AInstruction, SymbolTable


class TestCInstruction:
    def test_parsing(self):
        assert CInstruction.from_line("A=M") == CInstruction(
            dest="A", comp="M"
        )
        assert CInstruction.from_line("0;JMP") == CInstruction(
            comp="0", jump="JMP"
        )


class TestAInstruction:
    def test_gen_code(self):
        st = SymbolTable()
        assert AInstruction(value_xor_label=0).gen_code(st) == "0000000000000000"
        assert AInstruction(value_xor_label=1).gen_code(st) == "0000000000000001"
        assert AInstruction(value_xor_label=255).gen_code(st) == "0000000011111111"
        assert AInstruction(value_xor_label=256).gen_code(st) == "0000000100000000"
