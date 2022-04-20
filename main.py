"""
    -- สมาชิก --

    เทจัสวี จักกี้ 1620704427
    ปริญญา วงษ์มณี 1620706752
    ปณิธาน คานพรหม 1620707552
    พิสิษฐ์ จันทวี 1620707560
"""

import LexicalSyntaxAnalysis as lsa
import pyperclip

program = lsa.Program()
program.analyzer("Example/Large_Num.py")

# Lexical
print("\n" + str.center(" Lexical ", 100, "="))
lex = program.getLexical()
for key in lex :
    print(key, lex[key])

# Syntax
print("\n" + str.center(" Syntax Structure ", 100, "="))
print(program)
pyperclip.copy(str(program))


# # Checking / Debug
# # create code from syntax structure
# print("\n" + str.center(" Code ", 100, "="))
# print(program.toCode())
# # run code
# print("\n" + str.center(" Output ", 100, "="))
# program.run()
# # generate code
# program.toFile("generate.py")