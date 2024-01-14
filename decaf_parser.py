import re
from decaf_lexer import tokens
from decaf_ast import *
from decaf_typecheck import *

class_table = dict()
constructor_table = dict()
method_table = dict()
field_table = dict()
var_tables = []
used_var_tables = []
class_names = []
field_id = 1
method_id = 7
constructor_id = 1
variable_id = 1
formal_names = []
formal_types = []
curr_method_type = None
curr_class_super = ""

# Initializing the standard Decaf objects: Out and In
scan_int = Method("scan_int", 1, "public", "static", [], Type("int"), dict(), BlockStmt([], 0, True))
scan_float = Method("scan_float", 2, "public", "static", [], Type("float"), dict(), BlockStmt([], 0, True))
method_table["In"] = [scan_int, scan_float]
class_names.append("In")
class_table["In"] = DecafClass("In", "", [], method_table["In"], [])

int_formal = Variable("i", 1, "formal", Type("int"))
float_formal = Variable("f", 1, "formal", Type("float"))
boolean_formal = Variable("b", 1, "formal", Type("boolean"))
string_formal = Variable("s", 1, "formal", Type("string"))
print_int = Method("print", 3, "public", "static", [int_formal], Type("void"), {"i": int_formal}, BlockStmt([], 0, True))
print_float = Method("print", 4, "public", "static", [float_formal], Type("void"), {"f": float_formal}, BlockStmt([], 0, True))
print_bool = Method("print", 5, "public", "static", [boolean_formal], Type("void"), {"b": boolean_formal}, BlockStmt([], 0, True))
print_string = Method("print", 6, "public", "static", [string_formal], Type("void"), {"s": string_formal}, BlockStmt([], 0, True))
method_table["Out"] = [print_int, print_float, print_bool, print_string]
class_names.append("Out")
class_table["Out"] = DecafClass("Out", "", [], method_table["Out"], [])


def p_program(p):
    '''program : class_decl program
        | empty
    '''

    p[0] = Program(class_table)


def p_empty(p):
    'empty : '

    pass


def p_class_decl(p):
    'class_decl : CLASS ID found_class_name extends_class LCURLY class_body_decl RCURLY'

    constructors_arr = []
    methods_arr = []
    fields_arr = []
    if p[2] in constructor_table:
        constructors_arr = constructor_table[p[2]]
    if p[2] in method_table:
        methods_arr = method_table[p[2]]
    if p[2] in field_table:
        fields_arr = field_table[p[2]]
    p[0] = DecafClass(p[2], p[4], constructors_arr, methods_arr, fields_arr)
    class_table[p[2]] = p[0]


def p_found_class_name(p):
    'found_class_name :'

    if p[-1] in class_names:
        print("Syntax Error (classes must have distinct names): detected on line " + str(p.lineno(-1)))
        exit()
    else:
        class_names.append(p[-1])


def p_extends_class(p):
    '''extends_class : EXTENDS ID
        | empty
    '''

    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = ""
    global curr_class_super
    curr_class_super = p[0]


def p_class_body_decl(p):
    '''class_body_decl : class_body_decl_type class_body_decl
        | class_body_decl_type
    '''

    p[0] = p[1]


def p_class_body_decl_type(p):
    '''class_body_decl_type : field_decl
        | method_decl
        | constructor_decl
    '''

    p[0] = p[1]


def p_field_decl(p):
    'field_decl : modifier var_decl'

    fields_arr = []
    global field_id
    for var in p[2]:
        var_name = var[1]
        var_type = var[0]
        visibility = p[1][0]
        applicability = p[1][1]
        fields_arr.append(Field(var_name, field_id, visibility, applicability, var_type))
        field_id += 1
    latest_class = class_names[-1]
    if latest_class not in field_table:
        field_table[latest_class] = fields_arr
    else:
        field_table[latest_class] += fields_arr


def p_modifier(p):
    'modifier : visibility optional_static'

    p[0] = (p[1], p[2])


def p_visibility(p):
    '''visibility : PUBLIC
        | PRIVATE
        | empty
    '''

    if p[1] == "public":
        p[0] = "public"
    else:
        p[0] = "private"


def p_optional_static(p):
    '''optional_static : STATIC
        | empty
    '''

    if p[1] == "static":
        p[0] = "static"
    else:
        p[0] = "instance"


def p_var_decl(p):
    'var_decl : type variables SEMICOLON'

    variables_arr = []
    var_names = []
    for var_name in p[2]:
        if var_name in var_names or (len(var_tables) > 0 and var_name in var_tables[-1]):
            print("Syntax Error (declared variables within a block must have distinct names): detected on line "
                  + str(p.lineno(2)))
            exit()
        var_names.append(var_name)
        variables_arr.append((p[1], var_name))
    p[0] = variables_arr


def p_type(p):
    '''type : INT
        | FLOAT
        | BOOLEAN
        | VOID
        | NULL
        | ID
    '''

    p[0] = Type(p[1])


def p_variables(p):
    'variables : variable additional_vars'

    p[0] = [p[1]] + p[2]


def p_variable(p):
    'variable : ID'

    p[0] = p[1]


def p_additional_vars(p):
    '''additional_vars : COMMA variable additional_vars
        | empty
    '''

    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_method_decl(p):
    'method_decl : modifier type ID found_method_type LPAREN formals RPAREN block'

    params = []
    global variable_id
    variable_id = 1
    for formal in p[6]:
        formal_name = formal[1]
        formal_type = formal[0]
        if formal_name in used_var_tables[-1]:
            print("Syntax Error (declared variables within a block must have distinct names): detected on line "
                  + str(p.lineno(6)))
            exit()
        new_var = Variable(formal_name, variable_id, "formal", formal_type)
        params.append(new_var)
        used_var_tables[-1][formal_name] = new_var
        variable_id += 1
    global method_id
    visibility = p[1][0]
    applicability = p[1][1]
    method = Method(p[3], method_id, visibility, applicability, params, p[2], used_var_tables[-1], p[8])
    latest_class = class_names[-1]
    if latest_class not in method_table:
        method_table[latest_class] = [method]
    else:
        method_table[latest_class].append(method)
    method_id += 1
    p[0] = method


def p_found_method_type(p):
    'found_method_type :'

    global curr_method_type
    curr_method_type = p[-2]


def p_constructor_decl(p):
    'constructor_decl : modifier ID LPAREN formals RPAREN block'

    params = []
    global variable_id
    variable_id = 1
    for formal in p[4]:
        formal_name = formal[1]
        formal_type = formal[0]
        if formal_name in used_var_tables[-1]:
            print("Syntax Error (declared variables within a block must have distinct names): detected on line "
                  + str(p.lineno(4)))
            exit()
        new_var = Variable(formal_name, variable_id, "formal", formal_type)
        params.append(new_var)
        used_var_tables[-1][formal_name] = new_var
        variable_id += 1
    global constructor_id
    visibility = p[1][0]
    constructor = Constructor(constructor_id, visibility, params, used_var_tables[-1], p[6])
    latest_class = class_names[-1]
    if latest_class not in constructor_table:
        constructor_table[latest_class] = [constructor]
    else:
        constructor_table[latest_class].append(constructor)
    constructor_id += 1
    p[0] = constructor


def p_formals(p):
    '''formals : formal_param additional_formal_params
        | empty
    '''

    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []
    formal_names.clear()
    formal_types.clear()
    for formal in p[0]:
        if formal[1] in formal_names:
            print("Syntax Error (declared variables within a block must have distinct names): detected on line "
                  + str(p.lineno(0)))
            exit()
        formal_names.append(formal[1])
        formal_types.append(formal[0])
    global variable_id
    variable_id = len(formal_names) + 1


def p_formal_param(p):
    'formal_param : type variable'

    p[0] = (p[1], p[2])


def p_additional_formal_params(p):
    '''additional_formal_params : COMMA formal_param additional_formal_params
        | empty
    '''

    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_block(p):
    'block : LCURLY new_scope stmt_section RCURLY'

    type_correct = check_type_correct("block", p)
    p[0] = BlockStmt(p[3], p.lineno(0), type_correct)
    used_var_tables.append(var_tables[-1])
    var_tables.pop()


def p_new_scope(p):
    'new_scope :'
    var_tables.append(dict())


def p_stmt_section(p):
    '''stmt_section : stmt stmt_section
        | empty
    '''

    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_stmt(p):
    '''stmt : if_stmt
        | while_stmt
        | for_stmt
        | return_stmt
        | stmt_expr SEMICOLON
        | BREAK SEMICOLON
        | CONTINUE SEMICOLON
        | block
        | var_decl
        | SEMICOLON
    '''

    if type(p[1]) is list:
        global variable_id
        for var in p[1]:
            var_name = var[1]
            var_type = var[0]
            new_var = Variable(var_name, variable_id, "local", var_type)
            var_tables[-1][var_name] = new_var
            variable_id += 1
        p[0] = p[1]
    elif p[1] == "break":
        p[0] = BreakStmt(p.lineno(1))
    elif p[1] == "continue":
        p[0] = ContinueStmt(p.lineno(1))
    elif p[1] == ";":
        p[0] = SkipStmt(p.lineno(1))
    else:
        p[0] = p[1]


def p_if_stmt(p):
    'if_stmt : IF LPAREN expr RPAREN stmt else_stmt'

    type_correct = check_type_correct("if", p)
    if not type_correct:
        print("Type Error (if-statement is not type correct): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = IfStmt(p[3], p[5], p[6], p.lineno(0), type_correct)


def p_else_stmt(p):
    '''else_stmt : ELSE stmt
        | empty
    '''

    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = SkipStmt(p.lineno(0))


def p_while_stmt(p):
    'while_stmt : WHILE LPAREN expr RPAREN stmt'

    type_correct = check_type_correct("while", p)
    if not type_correct:
        print("Type Error (while-statement is not type correct): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = WhileStmt(p[3], p[5], p.lineno(0), type_correct)


def p_for_stmt(p):
    'for_stmt : FOR LPAREN optional_stmt_expr SEMICOLON optional_expr SEMICOLON optional_stmt_expr RPAREN stmt'

    type_correct = check_type_correct("for", p)
    if not type_correct:
        print("Type Error (for-statement is not type correct): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = ForStmt(p[3], p[5], p[7], p[9], p.lineno(0), type_correct)


def p_return_stmt(p):
    'return_stmt : RETURN optional_expr SEMICOLON'

    type_correct = check_rtn_type_correct(p[2], curr_method_type, class_table)
    if not type_correct:
        print("Type Error (return-statement is not type correct): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = ReturnStmt(p[2], p.lineno(0), type_correct)


def p_optional_stmt_expr(p):
    '''optional_stmt_expr : stmt_expr
        | empty
    '''

    if p[1] is None:
        p[0] = SkipStmt(p.lineno(0))
    else:
        p[0] = p[1]


def p_optional_expr(p):
    '''optional_expr : expr
        | empty
    '''

    if p[1] is None:
        p[0] = SkipStmt(p.lineno(0))
    else:
        p[0] = p[1]


def p_stmt_expr(p):
    '''stmt_expr : assign_expr
        | method_invocation
    '''

    type_correct = check_type_correct("expr", p)
    if not type_correct:
        print("Type Error (expr-statement is not type correct): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = ExprStmt(p[1], p.lineno(0), type_correct)


def p_expr(p):
    '''expr : primary_expr
        | assign_expr
        | arith_expr
        | bool_expr
        | unary_expr
    '''

    p[0] = p[1]


def p_primary_expr(p):
    '''primary_expr : literal
        | THIS
        | SUPER
        | LPAREN expr RPAREN
        | new_object
        | left_hand_side
        | method_invocation
    '''

    if p[1] == "this":
        expr_type = determine_this_super_type("this", class_names[-1], curr_class_super)
        p[0] = ThisExpr(p.lineno(1), expr_type)
    elif p[1] == "super":
        expr_type = determine_this_super_type("super", class_names[-1], curr_class_super)
        if str(expr_type) == "error":
            print("Type Error (super-expression: current class has no super class): " +
                  "detected on line " + str(p.lineno(0)))
            exit()
        p[0] = SuperExpr(p.lineno(1), expr_type)
    elif p[1] == "(":
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_literal(p):
    '''literal : INT_CONST
        | FLOAT_CONST
        | STRING
        | NULL
        | TRUE
        | FALSE
    '''

    float_pattern = re.compile(r'[0-9]+\.[0-9]+')
    int_pattern = re.compile(r'[0-9]+')
    str_pattern = re.compile(r'"[^"(\n)]*"')

    if float_pattern.match(p[1]) is not None:
        expr_type = determine_type("float_const", p, class_table)
        p[0] = FloatConstant(p[1], p.lineno(1), expr_type)
    elif int_pattern.match(p[1]) is not None:
        expr_type = determine_type("int_const", p, class_table)
        p[0] = IntConstant(p[1], p.lineno(1), expr_type)
    elif str_pattern.match(p[1]) is not None:
        expr_type = determine_type("string_const", p, class_table)
        p[0] = StrConstant(p[1], p.lineno(1), expr_type)
    elif p[1] == "null":
        expr_type = determine_type("null", p, class_table)
        p[0] = NullConstant(p.lineno(1), expr_type)
    elif p[1] == "true":
        expr_type = determine_type("true_const", p, class_table)
        p[0] = TrueConstant(p.lineno(1), expr_type)
    elif p[1] == "false":
        expr_type = determine_type("false_const", p, class_table)
        p[0] = FalseConstant(p.lineno(1), expr_type)


def p_new_object(p):
    'new_object : NEW ID LPAREN arguments RPAREN'

    resolved_constructor = resolve_constructor_name(p, class_table, class_names[-1], constructor_table)
    expr_type = determine_new_object_type(p[2], resolved_constructor)
    if str(expr_type) == "error":
        print("Type Error (new-object-expression: name resolution failed): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = NewObjectExpr(p[2], p[4], p.lineno(0), expr_type, resolved_constructor.cid)


def p_left_hand_side(p):
    'left_hand_side : field_access'

    p[0] = p[1]


def p_field_access(p):
    '''field_access : primary_expr DOT ID
        | ID
    '''

    if len(p) == 4:
        resolved_field = resolve_field_name(p, class_table, class_names[-1], curr_class_super, field_table)
        expr_type = determine_field_acc_type(resolved_field)
        if str(expr_type) == "error":
            print("Type Error (field-access-expression: name resolution failed): detected on line " + str(p.lineno(0)))
            exit()
        p[0] = FieldAccessExpr(p[1], p[3], p.lineno(0), expr_type, resolved_field.fid)
    else:
        if p[1] in var_tables[-1]:
            p[0] = VarExpr(var_tables[-1][p[1]].vid, p.lineno(1), Type(var_tables[-1][p[1]].var_type.name))
        else:
            found_variable = False
            for i in range(len(var_tables) - 2, -1, -1):
                if p[1] in var_tables[i]:
                    p[0] = VarExpr(var_tables[i][p[1]].vid, p.lineno(1), Type(var_tables[i][p[1]].var_type.name))
                    found_variable = True
                    break
            if not found_variable and p[1] in formal_names:
                for i in range(0, len(formal_names)):
                    if p[1] == formal_names[i]:
                        p[0] = VarExpr(i + 1, p.lineno(1), Type(formal_types[i].name))
                        found_variable = True
                        break
            if not found_variable and p[1] in class_names:
                expr_type = determine_class_ref_type(p[1], class_names[-1], class_table)
                if str(expr_type) == "error":
                    print("Type Error (class-ref-expression has wrong type): detected on line " + str(p.lineno(0)))
                    exit()
                p[0] = ClassReferenceExpr(p[1], p.lineno(1), expr_type)
                found_variable = True
            if not found_variable:
                print("Syntax Error (undeclared variable " + p[1] + "): detected on line " + str(p.lineno(1)))
                exit()


def p_method_invocation(p):
    'method_invocation : primary_expr DOT ID LPAREN arguments RPAREN'

    resolved_method = resolve_method_name(p, class_table, class_names[-1], curr_class_super, method_table)
    expr_type = determine_method_call_type(resolved_method)
    if str(expr_type) == "error":
        print("Type Error (method-call-expression: name resolution failed): detected on line " + str(p.lineno(0)))
        exit()
    p[0] = MethodCallExpr(p[1], p[3], p[5], p.lineno(0), expr_type, resolved_method.mid)


def p_arguments(p):
    '''arguments : expr additional_exprs
        | empty
    '''

    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_additional_exprs(p):
    '''additional_exprs : COMMA expr additional_exprs
        | empty
    '''

    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_assign_expr(p):
    '''assign_expr : left_hand_side ASSIGN_OP expr
        | left_hand_side INCREMENT
        | INCREMENT left_hand_side
        | left_hand_side DECREMENT
        | DECREMENT left_hand_side
    '''

    if len(p) == 4:
        expr_type = determine_type("assign", p, class_table)
        if str(expr_type) == "error":
            print("Type Error (assign-expression: one or more expressions have errors): " +
                  "detected on line " + str(p.lineno(0)))
            exit()
        p[0] = AssignExpr(p[1], p[3], p.lineno(0), expr_type)
    else:
        expr_type = determine_type("auto", p, class_table)
        if str(expr_type) == "error":
            print("Type Error (auto-expression: expression's type must be int or float): " +
                  "detected on line " + str(p.lineno(0)))
            exit()
        if p[1] == "++":
            p[0] = AutoExpr(p[2], "inc", "pre", p.lineno(0), expr_type)
        elif p[1] == "--":
            p[0] = AutoExpr(p[2], "dec", "pre", p.lineno(0), expr_type)
        elif p[2] == "++":
            p[0] = AutoExpr(p[1], "inc", "post", p.lineno(0), expr_type)
        elif p[2] == "--":
            p[0] = AutoExpr(p[1], "dec", "post", p.lineno(0), expr_type)


def p_arith_expr(p):
    '''arith_expr : expr PLUS expr
        | expr MINUS expr
        | expr MULTIPLY expr
        | expr DIVIDE expr
    '''

    expr_type = determine_type("binary", p, class_table)
    if str(expr_type) == "error":
        print("Type Error (binary-expression has wrong type): detected on line " + str(p.lineno(0)))
        exit()
    if p[2] == "+":
        p[0] = BinaryExpr(p[1], "add", p[3], p.lineno(0), expr_type)
    elif p[2] == "-":
        p[0] = BinaryExpr(p[1], "sub", p[3], p.lineno(0), expr_type)
    elif p[2] == "*":
        p[0] = BinaryExpr(p[1], "mul", p[3], p.lineno(0), expr_type)
    elif p[2] == "/":
        p[0] = BinaryExpr(p[1], "div", p[3], p.lineno(0), expr_type)


def p_bool_expr(p):
    '''bool_expr : expr AND expr
        | expr OR expr
        | expr EQUAL_TO expr
        | expr NOT_EQUAL_TO expr
        | expr LESS_THAN expr
        | expr GREATER_THAN expr
        | expr LESS_OR_EQUAL_TO expr
        | expr GREATER_OR_EQUAL_TO expr
    '''

    expr_type = determine_type("binary", p, class_table)
    if str(expr_type) == "error":
        print("Type Error (binary-expression has wrong type): detected on line " + str(p.lineno(0)))
        exit()
    if p[2] == "&&":
        p[0] = BinaryExpr(p[1], "and", p[3], p.lineno(0), expr_type)
    elif p[2] == "||":
        p[0] = BinaryExpr(p[1], "or", p[3], p.lineno(0), expr_type)
    elif p[2] == "==":
        p[0] = BinaryExpr(p[1], "eq", p[3], p.lineno(0), expr_type)
    elif p[2] == "!=":
        p[0] = BinaryExpr(p[1], "neq", p[3], p.lineno(0), expr_type)
    elif p[2] == "<":
        p[0] = BinaryExpr(p[1], "lt", p[3], p.lineno(0), expr_type)
    elif p[2] == "<=":
        p[0] = BinaryExpr(p[1], "leq", p[3], p.lineno(0), expr_type)
    elif p[2] == ">":
        p[0] = BinaryExpr(p[1], "gt", p[3], p.lineno(0), expr_type)
    elif p[2] == ">=":
        p[0] = BinaryExpr(p[1], "geq", p[3], p.lineno(0), expr_type)


def p_unary_expr(p):
    '''unary_expr : PLUS expr %prec UPLUS
        | MINUS expr %prec UMINUS
        | NEGATION expr
    '''

    expr_type = determine_type("unary", p, class_table)
    if str(expr_type) == "error":
        print("Type Error (unary-expression has wrong type): detected on line " + str(p.lineno(0)))
        exit()
    if p[1] == "-":
        p[0] = UnaryExpr("uminus", p[2], p.lineno(0), expr_type)
    elif p[1] == "!":
        p[0] = UnaryExpr("neg", p[2], p.lineno(0), expr_type)
    else:
        p[0] = UnaryExpr("", p[2], p.lineno(0), expr_type)


precedence = (
    ('right', 'ASSIGN_OP'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUAL_TO', 'NOT_EQUAL_TO'),
    ('nonassoc', 'LESS_THAN', 'GREATER_THAN', 'LESS_OR_EQUAL_TO', 'GREATER_OR_EQUAL_TO'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'UPLUS', 'UMINUS'),
    ('right', 'NEGATION')
)


def p_error(p):
    if p is None:
        print("Syntax Error: end of file reached.")
    else:
        print("Syntax Error: detected on line " + str(p.lineno))
    exit()
