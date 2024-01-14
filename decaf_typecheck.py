from decaf_ast import *


def is_subtype(type1, type2, class_table, strict):
    type1_str = str(type1)
    type2_str = str(type2)
    t1_is_class_lit = type1_str.startswith("class-literal(")
    t2_is_class_lit = type2_str.startswith("class-literal(")
    t1_is_user_def = type1_str.startswith("user(")
    t2_is_user_def = type2_str.startswith("user(")

    if type1_str == type2_str:
        return True
    elif t1_is_class_lit and t2_is_class_lit:
        type1_str = type1_str[type1_str.find("(") + 1:type1_str.find(")")]
        type2_str = type2_str[type2_str.find("(") + 1:type2_str.find(")")]
        if strict:
            return class_table[type1_str].super_name == type2_str
        else:
            return class_table[type1_str].super_name == type2_str or type1_str == class_table[type2_str].super_name
    elif t1_is_class_lit ^ t2_is_class_lit:
        return False
    elif t1_is_user_def and t2_is_user_def:
        type1_str = type1.name
        type2_str = type2.name
        if strict:
            return class_table[type1_str].super_name == type2_str
        else:
            return class_table[type1_str].super_name == type2_str or type1_str == class_table[type2_str].super_name
    elif t1_is_user_def ^ t2_is_user_def:
        if strict:
            return type1_str == "null" and t2_is_user_def
        else:
            return (t1_is_user_def and type2_str == "null") or (type1_str == "null" and t2_is_user_def)
    else:
        if strict:
            return type1_str == "int" and type2_str == "float"
        else:
            return (type1_str == "int" and type2_str == "float") or (type1_str == "float" and type2_str == "int")


def check_type_correct(stmt_kind, p):
    if stmt_kind == "if":
        return str(p[3].expr_type) == "boolean" and (not type_corr_exists(p[5]) or p[5].is_type_correct) and \
               (not type_corr_exists(p[6]) or p[6].is_type_correct)
    elif stmt_kind == "while":
        return str(p[3].expr_type) == "boolean" and (not type_corr_exists(p[5]) or p[5].is_type_correct)
    elif stmt_kind == "for":
        cond_expr_type = isinstance(p[5], SkipStmt) or str(p[5].expr_type) == "boolean"
        init_expr_type_corr = not type_corr_exists(p[3]) or p[3].is_type_correct
        update_expr_type_corr = not type_corr_exists(p[7]) or p[7].is_type_correct
        loop_body_type_corr = not type_corr_exists(p[9]) or p[9].is_type_correct
        return cond_expr_type and init_expr_type_corr and update_expr_type_corr and loop_body_type_corr
    elif stmt_kind == "expr":
        return str(p[1].expr_type) != "error"
    elif stmt_kind == "block":
        for stmt in p[3]:
            if type_corr_exists(stmt) and not stmt.is_type_correct:
                return False
        return True


def type_corr_exists(stmt):
    if isinstance(stmt, (IfStmt, WhileStmt, ForStmt, ReturnStmt, ExprStmt, BlockStmt)):
        return True
    else:
        return False


def check_rtn_type_correct(expr, rtn_type, class_table):
    if isinstance(expr, SkipStmt):
        return str(rtn_type) == "void"
    else:
        return str(expr.expr_type) != "error" and is_subtype(expr.expr_type, rtn_type, class_table, True)


def determine_type(expr_kind, p, class_table):
    if expr_kind == "int_const":
        return Type("int")
    elif expr_kind == "float_const":
        return Type("float")
    elif expr_kind == "string_const":
        return Type("string()")
    elif expr_kind == "true_const":
        return Type("boolean")
    elif expr_kind == "false_const":
        return Type("boolean")
    elif expr_kind == "null":
        return Type("null")
    elif expr_kind == "unary":
        if (p[1] == "+" or p[1] == "-") and (str(p[2].expr_type) == "int" or str(p[2].expr_type) == "float"):
            return Type(p[2].expr_type.name)
        elif p[1] == "!" and str(p[2].expr_type) == "boolean":
            return Type(p[2].expr_type.name)
        else:
            return Type("error()")
    elif expr_kind == "binary":
        type1_str = str(p[1].expr_type)
        type2_str = str(p[3].expr_type)
        if p[2] in ["+", "-", "*", "/"]:
            if type1_str == "int" and type2_str == "int":
                return Type("int")
            elif (type1_str == "int" and type2_str == "float") or \
                (type1_str == "float" and type2_str == "int") or \
                    (type1_str == "float" and type2_str == "float"):
                return Type("float")
            else:
                return Type("error()")
        elif p[2] in ["&&", "||"]:
            if type1_str == "boolean" and type2_str == "boolean":
                return Type("boolean")
            else:
                return Type("error()")
        elif p[2] in ["<", "<=", ">", ">="]:
            if (type1_str == "int" or type1_str == "float") and (type2_str == "int" or type2_str == "float"):
                return Type("boolean")
            else:
                return Type("error()")
        elif p[2] in ["==", "!="]:
            if is_subtype(p[1].expr_type, p[3].expr_type, class_table, False):
                return Type("boolean")
            else:
                return Type("error()")
    elif expr_kind == "assign":
        type1_str = str(p[1].expr_type)
        type2_str = str(p[3].expr_type)
        if type1_str != "error" and type2_str != "error" and \
                is_subtype(p[3].expr_type, p[1].expr_type, class_table, True):
            return Type(p[3].expr_type.name)
        else:
            return Type("error()")
    elif expr_kind == "auto":
        if (p[1] == "++" or p[1] == "--") and (str(p[2].expr_type) == "int" or str(p[2].expr_type) == "float"):
            return Type(p[2].expr_type.name)
        elif (p[2] == "++" or p[2] == "--") and (str(p[1].expr_type) == "int" or str(p[1].expr_type) == "float"):
            return Type(p[1].expr_type.name)
        else:
            return Type("error()")


def determine_field_acc_type(resolved_field):
    if resolved_field is not None:
        return Type(resolved_field.field_type.name)
    else:
        return Type("error()")


def determine_method_call_type(resolved_method):
    if resolved_method is not None:
        return Type(resolved_method.rtn_type.name)
    else:
        return Type("error()")


def determine_new_object_type(class_name, resolved_constructor):
    if resolved_constructor is not None:
        return Type(class_name)
    else:
        return Type("error()")


def determine_this_super_type(expr_kind, curr_class, curr_class_super):
    if expr_kind == "this":
        return Type(curr_class)
    elif expr_kind == "super":
        if curr_class_super == "":
            return Type("error()")
        else:
            return Type(curr_class_super)


def determine_class_ref_type(class_name, curr_class, class_table):
    if class_name == curr_class or class_name in class_table:
        return Type("class-literal(" + class_name + ")")
    else:
        return Type("error()")


def resolve_field_name(p, class_table, curr_class, curr_class_super, field_table):
    expr_type = p[1].expr_type
    expr_type_name = expr_type.name
    match_applicability = ""
    if str(expr_type).startswith("user("):
        match_applicability = "instance"
    elif str(expr_type).startswith("class-literal("):
        expr_type_name = expr_type_name[expr_type_name.find("(") + 1:expr_type_name.find(")")]
        match_applicability = "static"
    else:
        return None

    if expr_type_name in field_table:
        fields_arr = field_table[expr_type_name]
        for field in fields_arr:
            if (expr_type_name == curr_class and field.name == p[3] and field.applicability == match_applicability) or \
                (expr_type_name != curr_class and field.name == p[3] and field.visibility == "public" and
                    field.applicability == match_applicability):
                return field

        curr_super = curr_class_super
        if expr_type_name != curr_class:
            curr_super = class_table[expr_type_name].super_name
        while curr_super != "":
            fields_arr = field_table[curr_super]
            for field in fields_arr:
                if field.name == p[3] and field.visibility == "public" and field.applicability == match_applicability:
                    return field
            curr_super = class_table[curr_super].super_name
        return None
    else:
        return None


def resolve_method_name(p, class_table, curr_class, curr_class_super, method_table):
    expr_type = p[1].expr_type
    expr_type_name = expr_type.name
    match_applicability = ""
    if str(expr_type).startswith("user("):
        match_applicability = "instance"
    elif str(expr_type).startswith("class-literal("):
        expr_type_name = expr_type_name[expr_type_name.find("(") + 1:expr_type_name.find(")")]
        match_applicability = "static"
    else:
        return None

    if expr_type_name in method_table:
        methods_arr = method_table[expr_type_name]
        args = p[5]
        for method in methods_arr:
            params = method.parameters
            if (expr_type_name == curr_class and method.name == p[3] and
                    method.applicability == match_applicability and len(params) == len(args)) or \
                (expr_type_name != curr_class and method.name == p[3] and method.visibility == "public" and
                    method.applicability == match_applicability and len(params) == len(args)):
                args_match_params = True
                for i in range(0, len(params)):
                    if not is_subtype(args[i].expr_type, params[i].var_type, class_table, True):
                        args_match_params = False
                        break
                if args_match_params:
                    return method

        curr_super = curr_class_super
        if expr_type_name != curr_class:
            curr_super = class_table[expr_type_name].super_name
        while curr_super != "":
            methods_arr = method_table[curr_super]
            for method in methods_arr:
                params = method.parameters
                if method.name == p[3] and method.visibility == "public" and \
                        method.applicability == match_applicability and len(params) == len(args):
                    args_match_params = True
                    for i in range(0, len(params)):
                        if not is_subtype(args[i].expr_type, params[i].var_type, class_table, True):
                            args_match_params = False
                            break
                    if args_match_params:
                        return method
            curr_super = class_table[curr_super].super_name
        return None
    else:
        return None


def resolve_constructor_name(p, class_table, curr_class, constructor_table):
    class_name = p[2]

    if class_name in constructor_table:
        constructors_arr = constructor_table[class_name]
        args = p[4]
        for constructor in constructors_arr:
            params = constructor.parameters
            if (class_name == curr_class and len(params) == len(args)) or \
                    (class_name != curr_class and constructor.visibility == "public" and len(params) == len(args)):
                args_match_params = True
                for i in range(0, len(params)):
                    if not is_subtype(args[i].expr_type, params[i].var_type, class_table, True):
                        args_match_params = False
                        break
                if args_match_params:
                    return constructor
        return None
    else:
        return None

