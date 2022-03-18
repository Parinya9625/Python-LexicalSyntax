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