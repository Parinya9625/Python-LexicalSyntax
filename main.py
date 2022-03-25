"""
    -- สมาชิก --

    เทจัสวี จักกี้ 1620704427
    ปริญญา วงษ์มณี 1620706752
    ปณิธาน คานพรหม 1620707552
    พิสิษฐ์ จันทวี 1620707560
"""

import LexicalSyntaxAnalysis as lsa

program = lsa.Program()
program.analyzer("testcase.py")

print("\n" + str.center(" Lexical ", 100, "="))
print(program.getLexical())
print("\n" + str.center(" Syntax Structure ", 100, "="))
print(program)
print("\n" + str.center(" Code ", 100, "="))
print(program.toCode())
print("\n" + str.center(" Output ", 100, "="))
program.run()
# Generate code from syntax structure
program.toFile("generate.py")