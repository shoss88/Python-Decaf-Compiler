* decaf_lexer.py contains the lexing specifications, including tokens, reserved words, and token specifications.

* decaf_parser.py contains the parsing specifications, including production rules, and precedence specification.

* decaf_checker.py contains the main Python function that combines the lexer and parser from decaf_lexer.py and decaf_parser.py, respectively. decaf_checker.py takes input from the decaf file on the command line and checks the file's syntax. If the decaf file is syntactically correct, decaf_checker.py prints "Yes", otherwise it will print the first error and its location.

* decaf_ast.py contains the class definitions for each Decaf AST Node.

* decaf_typecheck.py contains the definitions for evaluating type constraints and name resolution.

* run the compiler in command prompt like so: python decaf_checker.py examplefilename.txt
