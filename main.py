import lexer

with open("program.txt") as file:  
	data = file.read() 

result, error, symbolTable = lexer.run('program', data)

if error: print(error.as_string())
else: 
	for token in result:
		print(token)
if not error:
	print("\n\n Below is our Symbol Table \n\n")
	print("Name\tAddress \t\tType\n")
	for entry in symbolTable:
		print(entry + "\t"+ str(symbolTable[entry]["address"]) + "\t" + str(symbolTable[entry]["dataType"]))