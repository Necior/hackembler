from hackembler import CInstruction, AInstruction


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
        assert AInstruction(value=0).gen_code() == "0000000000000000"
        assert AInstruction(value=1).gen_code() == "0000000000000001"
        assert AInstruction(value=255).gen_code() == "0000000011111111"
        assert AInstruction(value=256).gen_code() == "0000000100000000"
