class Node():
    def __init__(self):
        self.parent = None


class Program(Node):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes

        for decaf_class in self.classes:
            self.classes[decaf_class].parent = self

    def __str__(self):
        result = ""
        for decaf_class in self.classes:
            result += str(self.classes[decaf_class])
            result += "\n--------------------------------------------------------------------------\n"
        return result


class DecafClass(Node):
    def __init__(self, name, super_name, constructors, methods, fields):
        super().__init__()
        self.name = name
        self.super_name = super_name
        self.constructors = constructors
        self.methods = methods
        self.fields = fields

        for constructor in self.constructors:
            constructor.parent = self
            constructor.name = self.name
        for method in self.methods:
            method.parent = self
            method.class_name = self.name
        for field in self.fields:
            field.parent = self
            field.class_name = self.name

    def __str__(self):
        fields_str = "Fields:\n"
        for field in self.fields:
            fields_str += str(field) + "\n"
        constructors_str = "Constructors:\n"
        for constructor in self.constructors:
            constructors_str += str(constructor) + "\n"
        methods_str = "Methods:\n"
        for method in self.methods:
            methods_str += str(method) + "\n"
        result = "Class name: " + self.name + "\n" + "Super class name: " + self.super_name + "\n" \
                 + fields_str + constructors_str + methods_str
        return result


class Constructor(Node):
    def __init__(self, cid, visibility, parameters, var_table, body):
        super().__init__()
        self.name = ""
        self.cid = cid
        self.visibility = visibility
        self.parameters = parameters
        self.var_table = var_table
        self.body = body

        for param in self.parameters:
            param.parent = self
        for var in self.var_table:
            self.var_table[var].parent = self
        self.body.parent = self

    def __str__(self):
        result = "CONSTRUCTOR: " + str(self.cid) + ", " + self.visibility + "\n"
        parameters_str = "Constructor parameters: "
        for i in range(len(self.parameters)):
            parameters_str += str(self.parameters[i].vid)
            if i < len(self.parameters) - 1:
                parameters_str += ", "
        formals_str = ""
        locals_str = ""
        for var in self.var_table:
            if self.var_table[var].kind == "formal":
                formals_str += str(self.var_table[var]) + "\n"
            else:
                locals_str += str(self.var_table[var]) + "\n"

        variables_str = "Variable Table:\n" + formals_str + locals_str
        statements_str = "Constructor Body:" + str(self.body)
        result += parameters_str + "\n" + variables_str + statements_str
        return result


class Method(Node):
    def __init__(self, name, mid, visibility, applicability, parameters, rtn_type, var_table, body):
        super().__init__()
        self.name = name
        self.mid = mid
        self.class_name = ""
        self.visibility = visibility
        self.applicability = applicability
        self.parameters = parameters
        self.rtn_type = rtn_type
        self.var_table = var_table
        self.body = body

        for param in self.parameters:
            param.parent = self
        self.rtn_type.parent = self
        for var in self.var_table:
            self.var_table[var].parent = self
        self.body.parent = self

    def __str__(self):
        rtn_type_str = ""
        if self.rtn_type.name != "void":
            rtn_type_str += ", " + str(self.rtn_type)
        result = "METHOD: " + str(self.mid) + ", " + self.name + ", " + self.class_name + ", " \
                 + self.visibility + ", " + self.applicability + rtn_type_str + "\n"
        parameters_str = "Method parameters: "
        for i in range(len(self.parameters)):
            parameters_str += str(self.parameters[i].vid)
            if i < len(self.parameters) - 1:
                parameters_str += ", "
        formals_str = ""
        locals_str = ""
        for var in self.var_table:
            if self.var_table[var].kind == "formal":
                formals_str += str(self.var_table[var]) + "\n"
            else:
                locals_str += str(self.var_table[var]) + "\n"

        variables_str = "Variable Table:\n" + formals_str + locals_str
        statements_str = "Method Body:" + str(self.body)
        result += parameters_str + "\n" + variables_str + statements_str
        return result


class Field(Node):
    def __init__(self, name, fid, visibility, applicability, field_type):
        super().__init__()
        self.name = name
        self.fid = fid
        self.class_name = ""
        self.visibility = visibility
        self.applicability = applicability
        self.field_type = field_type

        self.field_type.parent = self

    def __str__(self):
        result = "FIELD: " + str(self.fid) + ", " + self.name + ", " + self.class_name + ", " \
                 + self.visibility + ", " + self.applicability + ", " + str(self.field_type)
        return result


class Variable(Node):
    def __init__(self, name, vid, kind, var_type):
        super().__init__()
        self.name = name
        self.vid = vid
        self.kind = kind
        self.var_type = var_type

        self.var_type.parent = self

    def __str__(self):
        result = "VARIABLE: " + str(self.vid) + ", " + self.name + ", " + self.kind + ", " + str(self.var_type)
        return result


class Type(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        result = ""
        if self.name == "error()":
            result = "error"
        elif self.name == "string()":
            result = "string"
        elif self.name.startswith("class-literal("):
            result = self.name
        elif self.name not in ["int", "float", "string", "boolean", "void", "null"]:
            result = "user(" + self.name + ")"
        else:
            result = self.name
        return result


class IfStmt(Node):
    def __init__(self, condition_expr, then_stmt, else_stmt, line_num, is_type_correct):
        super().__init__()
        self.condition_expr = condition_expr
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        self.condition_expr.parent = self
        self.then_stmt.parent = self
        self.else_stmt.parent = self

    def __str__(self):
        result = "\nIf(" + str(self.condition_expr) + ", " + str(self.then_stmt) + ", " \
                 + str(self.else_stmt) + ")"
        return result


class WhileStmt(Node):
    def __init__(self, condition_expr, body, line_num, is_type_correct):
        super().__init__()
        self.condition_expr = condition_expr
        self.body = body
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        self.condition_expr.parent = self
        self.body.parent = self

    def __str__(self):
        result = "\nWhile(" + str(self.condition_expr) + ", " + str(self.body) + ")"
        return result


class ForStmt(Node):
    def __init__(self, init_expr, condition_expr, update_expr, body, line_num, is_type_correct):
        super().__init__()
        self.init_expr = init_expr
        self.condition_expr = condition_expr
        self.update_expr = update_expr
        self.body = body
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        self.init_expr.parent = self
        self.condition_expr.parent = self
        self.update_expr.parent = self
        self.body.parent = self

    def __str__(self):
        result = "\nFor(" + str(self.init_expr) + ", " + str(self.condition_expr) + ", " \
                 + str(self.update_expr) + ", " + str(self.body) + ")"
        return result


class ReturnStmt(Node):
    def __init__(self, return_expr, line_num, is_type_correct):
        super().__init__()
        self.return_expr = return_expr
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        self.return_expr.parent = self

    def __str__(self):
        result = "\nReturn(" + str(self.return_expr) + ")"
        return result


class ExprStmt(Node):
    def __init__(self, expr, line_num, is_type_correct):
        super().__init__()
        self.expr = expr
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        self.expr.parent = expr

    def __str__(self):
        result = "\nExpr(" + str(self.expr) + ")"
        return result


class BlockStmt(Node):
    def __init__(self, statements, line_num, is_type_correct):
        super().__init__()
        self.statements = statements
        self.line_num = line_num
        self.is_type_correct = is_type_correct

        for stmt in self.statements:
            if type(stmt) is not list:
                stmt.parent = self

    def __str__(self):
        result = "\nBlock(["
        for i in range(len(self.statements)):
            stmt = self.statements[i]
            if type(stmt) is not list:
                result += str(stmt)
                if i < len(self.statements) - 1:
                    result += ", "
        return result + "\n])"


class BreakStmt(Node):
    def __init__(self, line_num):
        super().__init__()
        self.line_num = line_num

    def __str__(self):
        result = "\nBreak()"
        return result


class ContinueStmt(Node):
    def __init__(self, line_num):
        super().__init__()
        self.line_num = line_num

    def __str__(self):
        result = "\nContinue()"
        return result


class SkipStmt(Node):
    def __init__(self, line_num):
        super().__init__()
        self.line_num = line_num

    def __str__(self):
        result = "\nSkip()"
        return result


class IntConstant(Node):
    def __init__(self, value, line_num, expr_type):
        super().__init__()
        self.value = value
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(Integer-constant(" + self.value + "))"
        return result


class FloatConstant(Node):
    def __init__(self, value, line_num, expr_type):
        super().__init__()
        self.value = value
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(Float-constant(" + self.value + "))"
        return result


class StrConstant(Node):
    def __init__(self, value, line_num, expr_type):
        super().__init__()
        self.value = value
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(String-constant(" + self.value + "))"
        return result


class NullConstant(Node):
    def __init__(self, line_num, expr_type):
        super().__init__()
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(Null)"
        return result


class TrueConstant(Node):
    def __init__(self, line_num, expr_type):
        super().__init__()
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(True)"
        return result


class FalseConstant(Node):
    def __init__(self, line_num, expr_type):
        super().__init__()
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Constant(False)"
        return result


class VarExpr(Node):
    def __init__(self, ref_var_id, line_num, expr_type):
        super().__init__()
        self.ref_var_id = ref_var_id
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Variable(" + str(self.ref_var_id) + ")"
        return result


class UnaryExpr(Node):
    def __init__(self, unary_op, operand, line_num, expr_type):
        super().__init__()
        self.unary_op = unary_op
        self.operand = operand
        self.line_num = line_num
        self.expr_type = expr_type

        self.operand.parent = self
        self.expr_type.parent = self

    def __str__(self):
        result = "Unary(" + self.unary_op + ", " + str(self.operand) + ")"
        return result


class BinaryExpr(Node):
    def __init__(self, operand_1, binary_op, operand_2, line_num, expr_type):
        super().__init__()
        self.operand_1 = operand_1
        self.binary_op = binary_op
        self.operand_2 = operand_2
        self.line_num = line_num
        self.expr_type = expr_type

        self.operand_1.parent = self
        self.operand_2.parent = self
        self.expr_type.parent = self

    def __str__(self):
        result = "Binary(" + self.binary_op + ", " + str(self.operand_1) + ", " \
                 + str(self.operand_2) + ")"
        return result


class AssignExpr(Node):
    def __init__(self, lhs, rhs, line_num, expr_type):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
        self.line_num = line_num
        self.expr_type = expr_type

        self.lhs.parent = self
        self.rhs.parent = self
        self.expr_type.parent = self

    def __str__(self):
        result = "Assign(" + str(self.lhs) + ", " + str(self.rhs) + ", " + str(self.lhs.expr_type) + ", " \
                 + str(self.rhs.expr_type) + ")"
        return result


class AutoExpr(Node):
    def __init__(self, expr, auto_op, post_pre, line_num, expr_type):
        super().__init__()
        self.expr = expr
        self.auto_op = auto_op
        self.post_pre = post_pre
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr.parent = self
        self.expr_type.parent = self

    def __str__(self):
        result = "Auto(" + str(self.expr) + ", " + self.auto_op + ", " + self.post_pre + ")"
        return result


class FieldAccessExpr(Node):
    def __init__(self, base, field_name, line_num, expr_type, resolved_id):
        super().__init__()
        self.base = base
        self.field_name = field_name
        self.line_num = line_num
        self.expr_type = expr_type
        self.resolved_id = resolved_id

        self.base.parent = self
        self.expr_type.parent = self

    def __str__(self):
        result = "Field-access(" + str(self.base) + ", " + self.field_name + ", " + str(self.resolved_id) + ")"
        return result


class MethodCallExpr(Node):
    def __init__(self, base, method_name, args, line_num, expr_type, resolved_id):
        super().__init__()
        self.base = base
        self.method_name = method_name
        self.args = args
        self.line_num = line_num
        self.expr_type = expr_type
        self.resolved_id = resolved_id

        self.base.parent = self
        for arg in self.args:
            arg.parent = self
        self.expr_type.parent = self

    def __str__(self):
        args_str = "["
        for i in range(len(self.args)):
            args_str += str(self.args[i])
            if i < len(self.args) - 1:
                args_str += ", "
        args_str += "]"
        result = "Method-call(" + str(self.base) + ", " + self.method_name + ", " + \
                 str(self.resolved_id) + ", " + args_str + ")"
        return result


class NewObjectExpr(Node):
    def __init__(self, class_name, args, line_num, expr_type, resolved_id):
        super().__init__()
        self.class_name = class_name
        self.args = args
        self.line_num = line_num
        self.expr_type = expr_type
        self.resolved_id = resolved_id

        for arg in self.args:
            arg.parent = self
        self.expr_type.parent = self

    def __str__(self):
        args_str = "["
        for i in range(len(self.args)):
            args_str += str(self.args[i])
            if i < len(self.args) - 1:
                args_str += ", "
        args_str += "]"
        result = "New-object(" + str(self.class_name) + ", " + str(self.resolved_id) + ", " + args_str + ")"
        return result


class ThisExpr(Node):
    def __init__(self, line_num, expr_type):
        super().__init__()
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "This()"
        return result


class SuperExpr(Node):
    def __init__(self, line_num, expr_type):
        super().__init__()
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Super()"
        return result


class ClassReferenceExpr(Node):
    def __init__(self, class_name, line_num, expr_type):
        super().__init__()
        self.class_name = class_name
        self.line_num = line_num
        self.expr_type = expr_type

        self.expr_type.parent = self

    def __str__(self):
        result = "Class-reference(" + self.class_name + ")"
        return result





