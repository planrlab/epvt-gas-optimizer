from copy import deepcopy
from functools import reduce
from builtins import staticmethod
    

class Expression:
    gas_requirement = {
        '-'  : 3,
        '+'  : 3,
        '>'  : 3,
        '*'  : 5,
        '/'  : 5,
        'O'  : 3,
        'D'  : 5,
        '<'  : 3,
        'u-' : 3,
        '==' : 3,
        'AM' : 0,
        }
    
    def __init__(self, uid, operator, operands, value, wt):
        self.__operator = operator
        self.__operands = operands
        self.__uid = uid
        self.__value = value
        no_of_operands = len(operands)
        self.__wt = wt +(no_of_operands-1)*(self.gas_requirement.get(operator, 3)+self.gas_requirement.get('O'))
       
    def get_wt(self):
        return self.__wt
    
    def get_operands(self):
        return self.__operands
    
    def get_operator(self):
        return self.__operator
    
#     def get_value(self):
#         return reduce(lambda a, b: a*b, self.__operands)
    
    def get_value(self):
        return self.__value
    
    def get_uid(self):
        return self.__uid
    
    def set_uid(self, uid):
        self.__uid = uid
    
    def __repr__(self):
        return " id:" + str(self.__uid) +" opr:"+ str(self.__operator)+" opd:"+ str(self.__operands)+" wt:"+ str(self.__wt)
    

    
class BlockSTET:
    __equivalent_expressions = []
    expressions_list = []
    common_sub_expressions = dict()
    tokens = None
    optimized_expression = None
    __prime_numbers = []
    scope_info = dict()
    scope_id = -1
    __location_info = None
    __primes_generator  = None
    __current_uid = 2
    
    def __init__(self, _parent = None):
        self.memoizer = dict()
        self.get_optimized_expr_operands = self.optimized_wt(self.get_optimized_expr_operands)
        self.__skip = set()
        self.__parent = _parent
        self.__redefined = []
        self.__declared = []
        self.__expressions = dict() #id to object map
        self.__st = dict()
        self.__et = dict()
        self.__st_lookup = dict()
        if self.__parent:
            self.__expressions = deepcopy(_parent.get_expressions(None))
            self.__st = deepcopy(_parent.get_st())
            self.__et = deepcopy(_parent.get_et(None))
            self.__skip = deepcopy(_parent.get_skip())
        self.__primes_generator = BlockSTET.__get_prime_number_generator()
        self.current_scope_id = self.update_scope()
        BlockSTET.scope_info[self.current_scope_id] = [self.__st, self.__et, self.__expressions]
            
    
    
    @classmethod
    def get_scope_information(cls, _scope_id):
        return cls.scope_info.get(_scope_id)
        
                
    @classmethod
    def update_scope(cls):
        cls.scope_id += 1
        return cls.scope_id


    def get_scope_id(self):
        return self.current_scope_id
    
    
    @classmethod
    def set_location_info(cls, location_info):
        cls.__location_info = location_info
    
    
    @classmethod
    def get_location_info(cls):
        return cls.__location_info
    
           
    @staticmethod
    def set_tokens(_tokens):
        BlockSTET.tokens = _tokens
     
          
    @classmethod
    def update_expressions(cls, str_expression):
        cls.__equivalent_expressions.append(str_expression)
    
        
    @classmethod
    def get_equivalent_expressions_list(cls):
        return cls.__equivalent_expressions     
    
          
    def set_skip(self, skip):
        self.__skip = skip
     
    
    def get_skip(self):
        return self.__skip
    
    
    def remove_from_skip(self, var):
        if var in self.__skip:
            self.__skip.remove(var)
    
    
    def modify_scope(self, _node, seq_no):
        defined = _node.get_dec_def()
        if len(defined) == 1: #and not a Loop increment/decrement can be handle in other way by reusing prime ids
            var = defined[0]
            self.update_var_id(var, seq_no)
            self.remove_from_skip(var)
        elif len(defined) > 1:
            raise Exception("Tuple declaration detected")
    
    
    def used_def_reset(self, used_defined_set, seq_no):
        for var in used_defined_set:
            self.update_var_id(var, seq_no)


    def update_var_id(self, var, ln):
        uid = next(self.__primes_generator)
        self.update_st(uid, str(var), ln)
            
        
    def re_assign_uids(self, defined_list, ln):
        for variable in set(defined_list):
            self.update_var_id(variable, ln)
            self.remove_from_skip(variable) 
           
    def get_expressions(self, line_no):
        if line_no:
            return dict(filter(lambda x: x[1][1]< line_no, self.__expressions.items()))
        return self.__expressions 
        
    def get_expressions_from_scope(self, line_no, scope_id = None):
        if scope_id:
            expressions  = self.get_scope_information(scope_id)[-1]
        else:
            expressions = self.__expressions
            
        if line_no:
            return dict(filter(lambda x: x[1][1]< line_no, expressions.items()))
        return expressions 
    
    
    def get_expression(self, e_id):
        return self.__expressions.get(e_id)[0] if e_id in self.__expressions else None
    
    
    def get_expression_from_scope(self, e_id, scope_id):
        expressions  = self.get_scope_information(scope_id)[-1]
        return expressions.get(e_id)[0] if e_id in expressions else None
    
    
    def add_expression(self, uid, expr, line_no, scope_id):
        _, et, expressions  = self.get_scope_information(scope_id)
        et[expr.get_operator()][expr.get_value()] = (expr, line_no)
        expressions[uid] = (expr,line_no)

     
    def update_expression(self, uid, operands, line_no, l_value, scope_id = None):
        if len(operands) == 1 and uid == operands[0]: #Due to Back substitution
            return
        else:
            if scope_id:
                _, et, expressions = self.get_scope_information(scope_id)
            else:
                et, expressions = self.__et, self.__expressions
                
            expr = expressions.pop(uid)[0]
            opr = expr.get_operator()
            value  = expr.get_value()
            old_id = expr.get_uid()
            popped  = None
                
            if value in et.get(opr):
                popped = et.get(opr).pop(value)
                if type(popped) is list:
                    popped = list(filter(lambda item: item[0].get_uid()!=uid,popped))
                elif popped[0].get_uid()==uid:
                    popped = None
            wt = 0
            for operand in operands:
                if operand in expressions and line_no > expressions.get(operand)[1]:# and operand not in self.__st for new_weights
                    wt = wt + expressions.get(operand)[0].get_wt()
            expression = Expression(uid, opr, operands, self.get_opds_value(operands, opr, expressions),wt)
            if popped:
                if type(popped) is list:
                    et[opr][expression.get_value()] = [*popped, (expression, line_no)]
                else:
                    et[opr][expression.get_value()] = [popped, (expression, line_no)]
            else:
                et[opr][expression.get_value()] = (expression, line_no)
            expressions[uid] = (expression, line_no)     
    
        
    def get_defined(self):
        return self.__redefined
    
    def get_declared(self):
        return self.__declared
    
    def get_parent(self):
        return self.__parent
    
    def get_current_uid(self):
        return self.__current_uid
    
    def get_prime_numbers(self):
        return self.__prime_numbers
    
    def set_st_lookup(self, line_no):
        return self.__st_lookup
    
    def get_st_lookup(self, line_no = None, exp_id = None):
        if line_no:
            st = dict(filter(lambda item: type(item[0]) is int and item[0] != exp_id and item[1][1]<= line_no, self.__st.items()))
            return st
        else:
            return self.__st
    
    
    def get_st(self, line_no = None, exp_id = None, scope_id =None):
        if scope_id:
            st = self.get_scope_information(scope_id)[0]
        else:
            st = self.__st
        if line_no:
            t_st = dict(filter(lambda item: item[1] and item[1][1]< line_no or (type(item[0]) is int and item[0] != exp_id and item[1][1]<= line_no), st.items()))
            return t_st
        return st
    
    
    def get_et(self, opr, line_no = None, scope_id = None):
        if scope_id:
            et = self.get_scope_information(scope_id)[1]
        else:
            et = self.__et
        if opr:
            t_et = et.get(opr, dict())
        else:
            return et
        
        if line_no and len(t_et):
            t_et = dict()
            for opr,d_items in et.items():
                for value, items in d_items.items():
                    if type(items) is list:
                        t_items = list(filter(lambda l_item:l_item[1] < line_no, items))
                        if t_items:
                            t_et[value] = t_items[0] if len(t_items) == 1 else t_items
                    elif items[1]<line_no:
                        t_et[value] = items 
        return t_et  
    
    
    def get_opds_value(self, operands, operator, expressions = None):
        t_uvalue = 1
        if not expressions:
            expressions = self.__expressions
            
        for opd in operands:
            expr = expressions.get(opd)
            if expr:
                expr = expr[0]
            if expr and operator == expr.get_operator():
                t_uvalue = t_uvalue*expr.get_value() 
            else:
                t_uvalue = t_uvalue*opd
        return t_uvalue
     
    
    def get_symbol_wt(self,uid):
        st = self.get_st()
        symbol_info = st.get(uid)
        if symbol_info:
            if (st.get(symbol_info[0])[0]) == uid:
                return 0
        expr = self.get_expressions(None).get(uid)
        #in case of used and defined
        if not expr:
            return 0
        return expr[0].get_wt() 
    
    
    @classmethod
    def init_backsubstitution(cls):
        cls.common_sub_expressions = dict()
        cls.__equivalent_expressions = []
        cls.expressions_list = []
    
    
    def add_cse(self, opr, value, wt):
        self.common_sub_expressions[opr] = self.common_sub_expressions.get(opr, dict())
        n, w, scope_id, location_info = self.common_sub_expressions.get(opr).get(value, (0,0,None, None))
        if not scope_id:
            scope_id = self.get_scope_id()
            
        if not location_info:
            location_info = self.get_location_info()
        
        self.common_sub_expressions[opr][value] = (n + 1,  w + wt, scope_id, location_info)               
    
    
    def update_cse(self, opr, value, n_value, wt):
        n, p_wt, scope_id, location_info = self.common_sub_expressions.get(opr, dict()).pop(value, (0,0,-1, None))
        if n:
            self.common_sub_expressions[opr][n_value] = (n+1, p_wt+wt, scope_id, location_info)
    
    def update_st(self, uid, l_value, ln, dnd = None):
        if not dnd:
            self.__st[uid] = (l_value, ln)
        
        self.__st[l_value] = (uid, ln)
        
          
    def report_symbol(self, key, ln = 0, decl = False, defi = False, _dnd = False):
        #local block declaration or definition
        n_entry = False
        if decl:
            uid = next(self.__primes_generator)
            n_entry = True
            defi = uid
            self.__declared.append(key)
        #assigning same uid as that of rhs expression
        if defi:
            if defi in self.__st:
                _dnd = True
                
            self.update_st(defi, key, ln, _dnd)
            
            if key not in self.get_declared():
                parent = self.get_parent()
                if parent:
                    parent.__redefined.append(key)
            return defi, n_entry
        
        else:
            symbol_info = self.get_st().get(key)    
            if not symbol_info:
                uid = next(self.__primes_generator)
                n_entry = True
                self.update_st(uid, key, ln)
            else:
                uid, line_no = symbol_info  
        return uid, n_entry
 
    
    def remove_duplicates(self, cses, value):
        processed = []
        distinct_cses = []
        for val, wt in cses:
            max_value = val**(processed.count(val)+1)
            if value >= max_value and value % max_value == 0:
                processed.append(val) 
                distinct_cses.append((val, wt))
        return distinct_cses
    
    
    
    def report_sub_expressions(self, exp_id, lvalue):
        temp_exp = self.get_expressions(None).get(exp_id)
        if temp_exp:
            exp = temp_exp[0]
            opds = exp.get_operands()
            opr = exp.get_operator()
            if opr not in ["AM", "TO"]:
                val = self.get_opds_value(opds, opr)
                cses = []
                opds_len = len(opds)
                opr_gas = 3
                for opd in opds:
                    temp = []
                    opd_wt = self.get_symbol_wt(opd)
                    for se,t_wt in cses:
                        t_wt = self.get_symbol_wt(se) if self.__is_prime(se) else t_wt
                        t_wt += opd_wt+Expression.gas_requirement.get(opr, 0)
                        if opd*se != val:
                            temp.append((opd*se, t_wt+opr_gas))
                        elif lvalue:
                            #In the case of back substitution
                            self.update_cse(opr, val, exp_id, t_wt)
                    cses.extend(temp) 
                    cses.insert(0, (opd, 0))
                    
                    #Extra...
                    if opd_wt:
                        sub_expr = self.get_expressions(None).get(opd)
                        if sub_expr:
                            sub_expr = sub_expr[0]
                        self.add_cse(sub_expr.get_operator(), sub_expr.get_value(), opd_wt)#reverse sub
                        self.report_sub_expressions(opd, False) #lvalue
                cses = cses[opds_len:]
                
                #Associative and Commutative Property
                if opds_len!=len(set(opds)) and opr in ['+', '*']:
                    cses = self.remove_duplicates(cses, val)
                
                for value, cs_wt in cses:
                    self.add_cse(opr, value, cs_wt)
    
    
    
    def regenerate_expression(self, exp_id, st, line_no = None, s_id = None):
        if exp_id in st:
            str_expression = st[exp_id][0]
            if str_expression.startswith("c_"):
                str_expression = str_expression[2:]
            else:
                if not str_expression.startswith("temp"):
                    str_expression = self.tokens.get(str_expression).get_variable_name()
                #raise RuntimeWarning("Need to Check this")
            return str_expression
            
        else:
            if s_id:
                expressions = self.get_scope_information(s_id)[-1]
            else:
                expressions = self.__expressions
            if line_no:
                rexpr = dict(filter(lambda x: x[1][1]< line_no, expressions.items()))
            else:
                rexpr = expressions
            rexpr = rexpr.get(exp_id)    
            
            if rexpr:
                rexpr = rexpr[0]
                opr = " " + rexpr.get_operator() + " "
                x = [self.regenerate_expression(opd, st, line_no, s_id) for opd in rexpr.get_operands()]
                if len(x)>1:
                    return opr.join(x)
                else:
                    operand = x[0]
                    opr = opr.strip()
                    if opr == 'u-':
                        return '(-'+ operand + ')'
                    elif opr == '!':
                        return '(!'+ operand + ')'
                    elif opr == '~':
                        return '(~'+ operand + ')'
                    else: # for +
                        return operand
            else:
                str_expression = self.get_st(scope_id = s_id)[exp_id][0]
                if str_expression.startswith("c_"):
                    str_expression = str_expression[2:]
                    return str_expression
                return self.tokens.get(str_expression).get_variable_name()
    
    def generate_ternary_exp(self, operands, line_no):
        exp = ":".join([str(self.generate_expression(opd, line_no, True)) for opd in operands])
        return exp.replace(":","?", 1)   
    
         
    def generate_member_exp(self, operands, line_no):
        st = self.get_st()
        exp = ""
        opr_name = ""
        mem_type = None
        if operands[0] in st:
            member_id = st[operands[0]][0]
            if isinstance(member_id, str) and not member_id.startswith("c_"): #if not constant
                opr_name, mem_type = self.get_member_info(member_id)
        else:
            if isinstance(operands, tuple) and len(operands) == 2:
                opr_name = self.generate_expression(operands[0], line_no, False)
                if isinstance(operands[1], list):
                    mem_type = "function"
                else:    
                    mem_type = "msg" #can be member access
        
        if mem_type: 
            if mem_type.endswith("]"):
                exp = opr_name + "".join([str("["+self.generate_expression(opd, line_no, False)+"]")for opd in operands[1:]])
             
            elif mem_type.startswith("mapping"):
                exp = opr_name + "".join([str("["+self.generate_expression(opd, line_no, False)+"]")for opd in operands[1:]])
             
            elif mem_type in ["function", "new"] or mem_type.startswith("type(") or mem_type.startswith("function ("):
                exp = opr_name+"("+", ".join([str(self.generate_expression(opd, line_no, False))for opd in operands[1]])+")"
                
            elif mem_type.startswith("struct ") or mem_type.startswith("address") or mem_type.startswith("contract ") or mem_type in ["msg", "tx", "abi", "block"]:
                exp = opr_name + "." + str(self.generate_expression(operands[1], line_no, False))
            
            else:
                raise Exception("Handle AM")
        else:
            exp = opr_name +"[" +",".join([str(self.generate_expression(opd, line_no, False))for opd in operands[:]]) +"]"    
        return exp
     
     
    def get_member_info(self, member_id):
        member = self.tokens.get(member_id)
        if hasattr(member, 'get_variable_name'):
            return member.get_variable_name(), member.get_type()
        else:
            return member.get_value(), member.get_type()
             
               
    def generate_expression(self, exp_id, line_no = None, sub_exp = False):
        st = self.get_st(None)
        if isinstance(exp_id, list):
            exp_id = exp_id[0]        
        if exp_id in st and st[exp_id][0] in st and st[st[exp_id][0]][0]==exp_id:
            str_expression = st[exp_id][0]
            if str_expression.startswith("c_"):
                str_expression = str_expression[2:]
            else:
                member = self.tokens.get(str_expression)
                if hasattr(member, 'get_variable_name'):
                    str_expression = member.get_variable_name()
                else:
                    str_expression =  member.get_value()
            return str_expression
         
        else:
            rexpr = self.get_expressions(None).get(exp_id)[0]
            opr = rexpr.get_operator()
            operands = rexpr.get_operands()
            if len(operands)>1:
                if isinstance(operands, tuple):
                    if opr == "AM":
                        return self.generate_member_exp(operands, line_no)
                    elif opr == "TO":
                        return self.generate_ternary_exp(operands, line_no)
                    else:
                        raise Exception("UNKNOWN")
                else:
                    opr = " "+rexpr.get_operator()+" " 
                    exp = opr.join([self.generate_expression(opd, line_no, True) for opd in operands])
                    if sub_exp:
                        exp = "("+exp+")"
                    return exp
            else:
                #To add support for other unary operators
                operand = self.generate_expression(operands[0], line_no)
                opr = opr.strip()
                if opr == 'u-':
                    return '(-'+ operand + ')'
                elif opr == '!':
                    return '(!'+ operand + ')'
                elif opr == '~':
                    return '(~'+ operand + ')'
                else: # for +
                    return operand
                        
    
    def get_exp_value_opr(self, n, opr):
        i = 2
        p_opds = []
        wt = 0
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                if i in self.__expressions:
                    wt+= self.__expressions.get(i)[0].get_wt()
                p_opds.append(i)
                exp = self.__et.get(opr, dict()).get(n, None)
                if exp:
                    exp = exp[0]
                    n = 1
                    wt+= exp.get_wt()
                    p_opds.append(exp.get_uid()) 
                    break
        if n > 1:
            if n in self.__expressions:
                    wt+= self.__expressions.get(n)[0].get_wt()
            p_opds.append(n)
        return Expression(None, opr, p_opds, self.get_opds_value(p_opds, opr), wt)

    
    def perform_backsubstitution(self, candidates):
        temp_types = dict()
        
        def get_temp_dataType(uid, sid):
            t_expression = self.get_expression_from_scope(uid, sid)
            
            if t_expression.get_operator() in ['+', '-', '*', '/']:
                ts = self.get_scope_information(sid)[0]
                t_vname = ts.get(t_expression.get_operands()[0])[0]
                oprn_obj = self.tokens.get(t_vname)
                return str(oprn_obj.get_type() + " ") if oprn_obj else temp_types.get(t_vname)
            else:
                raise Expression("Need to resolve data type of Temp expression")
                
        new_expr = []
        cse_ids = []
        t_id = 1
        uid = None
        self.memoizer = dict()
        declaration_section = []       
        for uid, e_weight, _, opr, _s_id, location_info in candidates:
            l_value = 'temp_'+str(t_id)
            condition = True
            
            if not self.__is_prime(uid):
                operands = self.get_all_opds(uid)
                uid = next(self.__primes_generator)
                wt = 0
                for operand in operands:
                    if operand in self.__expressions:# and operand not in self.__st for new_weights
                        wt = wt + self.__expressions[operand][0].get_wt() 
                t_expr = Expression(uid, opr, operands, self.get_opds_value(operands, opr), wt)
                location_info = (location_info[0], 0)
            else:
                t_expr = deepcopy(self.get_expression_from_scope(uid, _s_id))
            t_wt = t_expr.get_wt()
            if e_weight <= 13+t_wt: 
                condition = False 
            self.add_expression(uid, t_expr, 0, _s_id)
            
            if condition:
                if not l_value.startswith("temp"):
                    l_value = self.tokens.get(l_value).get_variable_name()
                exp = l_value+" = "+self.regenerate_expression(uid, self.get_st(1, uid, scope_id = _s_id), 0, s_id = _s_id)
                self.update_st(uid, l_value, 0)
                if exp.startswith("temp_"):
                    temp_type = get_temp_dataType(uid, _s_id)
                    declaration_section.append(temp_type+l_value)
                    temp_types[l_value] = temp_type
                new_expr.append((location_info,exp))
                cse_ids.append(uid)   
                t_id+=1
                
        if len(declaration_section):
            new_expr.insert(0, ";".join(declaration_section))
        
        for line_no, exp_id, l_value, _s_id in self.expressions_list:
            if l_value:
                rexpr = self.get_expression_from_scope(exp_id, _s_id)
                if rexpr:
                    operands = deepcopy(rexpr.get_operands())
                    e_value = rexpr.get_value()
                    opr = rexpr.get_operator()
                    t_operands, spl = self.get_optimized_expr_operands( e_value, opr, line_no, _s_id)
                    self.memoizer[(e_value, opr)] = ([exp_id], 1)
                    if operands and t_operands and reduce(lambda a,b: a*b, operands)!= reduce(lambda a,b: a*b,t_operands):
                        operands = t_operands 
                        self.update_expression(exp_id, operands, line_no, l_value, _s_id)
                    elif spl == 1:
                        self.update_expression(exp_id, operands, line_no, l_value, _s_id)
                if not l_value.startswith("temp"):
                    l_value = self.tokens.get(l_value).get_variable_name()
                else:
                    l_value = get_temp_dataType(exp_id) + l_value
                exp = l_value+" = "+self.regenerate_expression(exp_id, self.get_st(line_no, exp_id), s_id = _s_id)
                new_expr.append(exp)
            else:
                exp = self.regenerate_expression(exp_id, self.get_st(line_no, exp_id), s_id = _s_id)
                new_expr.append(exp)
        return new_expr
    
    
    def get_all_opds(self, n):
        i = 2
        p_opds = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                p_opds.append(i)
        if n > 1:
            p_opds.append(n)
        return p_opds

    
    def get_filtered_candidates(self, candidates, avl):
        positions = []
        for pos, candidate in enumerate(candidates):
            e_value = candidate[0]
            if self.get_expression(e_value):
                opds  = self.get_expression(e_value).get_operands() if self.__is_prime(e_value) else self.get_all_opds(e_value) 
            if e_value in avl and avl.get(e_value)<1:
                positions.insert(0, pos)
            elif not all([avl.get(opd, 1)>0 for opd in opds]):
                positions.insert(0, pos)
            else:
                count = candidate[1]//candidate[2]
                for opd in opds:
                    if opd in avl:
                        avl[opd] = avl.get(opd) - count
        
        for pos in positions:
            candidates.pop(pos)
        candidates.sort(key = lambda x: x[2]) 
        
        return candidates
        
        
    def optimize_available_expressions(self):
        threshold = 1
        cses = self.common_sub_expressions.items()
        candidates = []
        temp_count = dict()
        def get_position(wt, e_value = None):
            if len(candidates)==0:
                return 0
            else:
                for index, (cn_id, t_wt, e_wt, cn_opr,_,_) in enumerate(candidates):
                    if (t_wt-e_wt) < wt:
                        break
                    else:
                        index+=1                                    
                return index
            
        for opr, opr_dic in cses:
            """Skipping access member category for finding CSES"""
            if not opr in ["TO", "AM"]:
                for e_value, (e_count, e_twt, e_scope_id, location_info)  in opr_dic.items():
                    if e_count > threshold:    
                        expressions = self.get_expressions_from_scope(None, e_scope_id)
                        expr_obj = expressions.get(e_value)
                        e_wt = e_twt//e_count
                        savings = e_twt - e_wt
                        if expr_obj:
                            expr_obj = expr_obj[0]
                            temp_count[expr_obj.get_uid()] = e_count
                            if e_twt >= 13+expr_obj.get_wt(): 
                                candidates.insert(get_position(savings, e_value), (e_value, e_twt, e_wt, expr_obj.get_operator(), e_scope_id, location_info))
                        else:
                            expressions = self.__et.get(opr, dict())      
                            expr_obj = expressions.get(e_value)
                            if expr_obj:
                                if type(expr_obj) is list:
                                    expr_obj = expr_obj[0]
                                expr_obj = expr_obj[0]
                                temp_count[expr_obj.get_uid()] = e_count
                                if e_twt > 13+expr_obj.get_wt()+3:
                                    pos = get_position(savings, e_value)
                                    if pos>-1:
                                        candidates.insert(pos, (expr_obj.get_uid(), e_twt, e_wt, None, e_scope_id, location_info))
                            elif e_twt > 26:
                                pos = get_position(savings, e_value)
                                if pos>-1:
                                    candidates.insert(pos, (e_value, e_twt, e_wt, opr, e_scope_id, location_info))
                    if self.__is_prime(e_value):
                        temp_count[e_value] = e_count                               
        candidates = self.get_filtered_candidates(candidates,temp_count)
        if len(candidates)>0:
            return self.perform_backsubstitution(candidates)
        
    
    def calculate_wt(self, operator, opds, wt, s_id):
        no_of_operands = 0
        wt = 0
        for opd in opds:
            no_of_operands += 1
            if not self.get_st(scope_id=s_id).get(opd):
                wt += self.get_expression_from_scope(opd, s_id).get_wt() 
        return wt +(no_of_operands-1)*(Expression.gas_requirement.get(operator)+Expression.gas_requirement.get('O'))
        
    
    def optimized_wt(self, fun):
        def helper(e_value, opr, line_no, s_id):
            if (e_value,opr) not in self.memoizer:
                self.memoizer[(e_value, opr)] = deepcopy(fun(e_value, opr, line_no, s_id))
            return deepcopy(self.memoizer[(e_value, opr)])
        return helper
    
    
    def get_optimized_expr_operands(self, e_value, opr, line_no=None, s_id = None):
        expressions = None
        is_var_or_expr = self.__is_prime(e_value)
        if not is_var_or_expr:
            expressions =  self.get_et(opr, line_no)
            expression = expressions.get(e_value) 
            if expression:
                expression = expression[0]
                e_value = expression.get_uid()
                is_var_or_expr = True
            elif type(e_value) is str:
                return (None, None)
                
        if is_var_or_expr:        
            variable = self.get_st().get(e_value, False)
            if variable:
                return ([e_value], 1)
            else: #MemberAccess
                return (None, None)
                raise Exception("Not Available in ST")
        else:
            possible_sub_expressions = []
            opds = []
            
            t_expressions = [e_val for e_val in expressions if type(e_val) is int and e_value%e_val==0]
            if not t_expressions:
                return (None, None)
            
            for exp_val in t_expressions:
                wt = 0
                expression = expressions.get(exp_val)[0]
                if type(expression) is tuple:
                    expression = expression[0]
                sub_exp_value = e_value//exp_val
                if self.__is_prime(sub_exp_value):
                    opds = [expression.get_uid(), sub_exp_value]
                else:
                    opds, wt = self.get_optimized_expr_operands(sub_exp_value, opr, line_no, s_id)
                    if not wt:
                        opds = self.get_all_opds(sub_exp_value)
                    opds.append(expression.get_uid())
                possible_sub_expressions.append((opds, self.calculate_wt(opr, opds, wt, s_id)))
            possible_sub_expressions.sort(key = lambda x: x[1])
            return deepcopy(possible_sub_expressions[0])
        
    def report_expr(self, operator, t_operands, line_no):
        expression = None
        n_entry = False
        uvalue = self.get_opds_value(t_operands, operator)
  
        operands = self.__get_equivalent_expression(operator, uvalue, line_no=None)
        if not operands:
            operands = t_operands
            
        if type(operands) is Expression:
            expression = operands
        else:
            uvalue = self.get_opds_value(operands, operator)
            if not len(self.get_et(operator)):
                self.__et[operator] = dict()
            uid = next(self.__primes_generator)
            wt = 0
            for operand in operands:
                if operand in self.__expressions:# and operand not in self.__st for new_weights
                    wt = wt + self.__expressions[operand][0].get_wt()                    
            expression = Expression(uid, operator, operands, self.get_opds_value(operands, operator), wt)
            self.__et[operator][uvalue] = (expression, line_no)
            self.__expressions[expression.get_uid()] = (expression, line_no)
            n_entry = True
            self.memoizer[(uvalue, operator)] = ([uid], 1)
        return expression.get_uid(), n_entry, expression.get_wt()
    
    
    def __get_equivalent_expression(self, operator, uvalue, line_no=None):
        expression = None
        expressions = self.get_et(operator, line_no).get(uvalue)
        sym_table = self.get_st(line_no)
              
        if type(expressions) is list:
            for expr in expressions:
                exp_id = expr[0].get_uid()
                exp_info = sym_table.get(exp_id)
                if not exp_info or sym_table.get(exp_info[0])[0] == exp_id:
                    return expr[0]
                
        elif expressions:
            exp_id = expressions[0].get_uid()
            exp_info = sym_table.get(exp_id)
            if not exp_info or sym_table.get(exp_info[0])[0] == exp_id:
                expression = expressions[0]
                   
        if not expression:
            expression, _ = self.get_optimized_expr_operands(uvalue, operator, line_no, self.get_scope_id())                        
        return expression    
    
    @classmethod
    def __get_prime_number_generator(cls):
        if cls.__current_uid == 2 and cls.__current_uid not in BlockSTET.__prime_numbers:
            BlockSTET.__prime_numbers.append(cls.__current_uid)
            yield cls.__current_uid
            
        while True:
            cls.__current_uid += 1
            if cls.__is_prime(cls.__current_uid):
                BlockSTET.__prime_numbers.append(cls.__current_uid)
                yield cls.__current_uid
            
    @classmethod
    def __is_prime(self, number):
        if type(number) is int:
            for prime in self.__prime_numbers:
                if not (number == prime or number % prime):
                    return False
            return number
        return False
    
        
    def record_equivalent_expression(self, exp_id, lvalue, line_no=None):
        self.report_sub_expressions(exp_id, lvalue)
        str_expression = self.generate_expression(exp_id)      
        st = self.get_st()
        operands = None
        if lvalue:
            if st.get(lvalue):
                t_mem = eval(lvalue)
                if isinstance(t_mem, tuple):
                    operands, _ , _  = self.process_operands(t_mem, line_no)
                    lvalue = self.generate_member_exp(operands, line_no)
                else:
                    lvalue = self.tokens.get(lvalue).get_variable_name()
                        
                str_expression = lvalue + " = " + str_expression
            else:
                t = st.get(exp_id)
                self.__st[lvalue] = t
                t_mem = eval(lvalue)
                if isinstance(t_mem, tuple):
                    operands, _ , _  = self.process_operands(t_mem, line_no)
                    lvalue = self.generate_member_exp(operands, line_no)
                else:
                    lvalue = self.tokens.get(lvalue).get_variable_name()
                        
                str_expression = lvalue + " = " + str_expression
                
        self.__class__.__equivalent_expressions.append(str_expression)
        self.__class__.optimized_expression = str_expression
        return operands

    def reset(self):
        self.__class__.optimized_expression = None
        
         
    def process_expression(self, expression, line_no = None, sub_exp = True):   
        if isinstance(expression, dict):
            s_id = self.get_scope_id()
            l_value = None
            is_new = False
            operator, operands = tuple(expression.items())[0]
            index = 0
            if operator.strip() == "=":
                l_value = operands[index]
                index += 1
            
            #First process r_values
            operands_uids, n_count, wt = self.process_operands(operands[index:], line_no)    
            
            if not l_value:
                u_id, is_new, wt = self.report_expr(operator, operands_uids, line_no)
                if not sub_exp:
                    self.record_equivalent_expression(u_id, l_value, line_no)
                    self.expressions_list.append((line_no, u_id, l_value, s_id))                      
            else:
                u_id = operands_uids[0]
                if n_count==1:#and (not self.get_st(u_id) or not self.get_st(l_value)):
                    t_expression = self.get_expression(u_id)
                    u_id = next(self.__primes_generator)
                    e_opr = t_expression.get_operator()
                    e_value = t_expression.get_value()
                    e_wt = t_expression.get_wt()
                    expression = Expression(u_id, e_opr, operands_uids, e_value, e_wt)
                    avail = self.__et[e_opr].get(e_value)
                    if type(avail) is list:
                        self.__et[e_opr][e_value] = [*avail, (expression, line_no)]
                    else:
                        self.__et[e_opr][e_value] = [avail, (expression, line_no)]
                    self.__expressions[u_id] = (expression, line_no)
                    
                l_value = str(l_value)
                # Equivalent Expression
                
                n_l_value = self.record_equivalent_expression(u_id, l_value, line_no)
                dnd = False
                if n_l_value:
                    dnd = True
                    if type(n_l_value) is list:
                        l_value = str(tuple(n_l_value))
                    else:
                        raise Exception("Handle L_value type") 
                self.expressions_list.append((line_no, u_id, l_value, s_id))
                self.report_symbol(l_value, defi=u_id, ln = line_no, _dnd = dnd)
                #verify if current st_value gets updated or not
            return u_id, is_new, wt  
        
        elif isinstance(expression, int):
            """In case of Variable Declaration without Definition"""
            u_id, is_new = self.report_symbol(str(expression), ln = line_no)
            return u_id, is_new, 0
        
        elif isinstance(expression, str):
            u_id, is_new = self.report_symbol("c_"+expression, ln = line_no)
            return u_id, is_new, 0
        
        elif isinstance(expression, tuple):
            u_id, is_new, wt = self.process_member_access(expression, line_no = line_no)
            self.record_equivalent_expression(u_id, None, line_no)
            return u_id, is_new, wt
            
        else:
            raise Exception("Invalid Expression Intermediate Form:"+str(expression))
        
    
    
    def process_member_access(self, operand, line_no = None, sub_exp = False):
        #((21, 69), 5)
        wt = 0
        if isinstance(operand, tuple):
            uvalue = 1
            is_new = False
            if len(operand) == 1:
                member = operand[0]    
                if isinstance(member, dict):
                    uid, is_new, t_wt = self.process_expression(member, line_no)
                    uvalue *= uid
                    wt += t_wt
                    
                elif isinstance(member, tuple):
                    uid, is_new, _ = self.process_member_access(member, line_no)
                    uvalue *= uid
                
                else:
                    raise Expression("New Type In Operands")
            
            #Ternary operator
            else:
                if len(operand) == 3 and isinstance(operand[0], dict):
                    operator_type = "TO"
                    mem_imf = []
                    for member in operand:
                        if isinstance(member, int):
                            uid, _ = self.report_symbol(str(member), line_no)
                            uvalue *= uid
                            
                        elif isinstance(member, str):
                            uid, _ = self.report_symbol("c_"+str(member), line_no)  
                            uvalue *= uid
                              
                        elif isinstance(member, dict):
                            uid, _, t_wt = self.process_expression(member, line_no)
                            uvalue *= uid
                            wt += t_wt
                            
                        elif isinstance(member, tuple):
                            uid, _, _ = self.process_member_access(member, line_no)
                            uvalue *= uid
                        
                        elif isinstance(member, list):
                            uid, _, t_wt = self.process_operands(member, line_no)
                            wt += t_wt
                        else:
                            raise Expression("New Type In Operands")
                        mem_imf.append(uid)
                else:
                    operator_type = "AM"
                    mem_imf = []
                    for member in operand:
                        if isinstance(member, int):
                            uid, _ = self.report_symbol(str(member), line_no)
                            uvalue *= uid
                            
                        elif isinstance(member, str):
                            uid, _ = self.report_symbol("c_"+str(member), line_no)  
                            uvalue *= uid
                              
                        elif isinstance(member, dict):
                            uid, _, t_wt = self.process_expression(member, line_no)
                            uvalue *= uid
                            wt += t_wt
                            
                        elif isinstance(member, tuple):
                            uid, _, _ = self.process_member_access(member, line_no)
                            uvalue *= uid
                        
                        elif isinstance(member, list):
                            uid, _, t_wt = self.process_operands(member, line_no)
                            wt += t_wt
                        else:
                            raise Expression("New Type In Operands")
                        mem_imf.append(uid)
                    
                uid, is_new, wt = self.access_member(operator_type, tuple(mem_imf), line_no)   
            return uid, is_new, wt
            
            
    def access_member(self, operator, operands, line_no):
        uvalue = str(operands)
        members = self.get_et(operator, line_no).get(uvalue)
        sym_table = self.get_st(line_no)
        is_new = True
        if members:
            is_new = False
            if  not isinstance(members, list):
                members = [members]
        
            for expr in members:
                expression = expr[0]
                exp_id = expression.get_uid()
                exp_info = sym_table.get(exp_id)
                if not exp_info or sym_table.get(exp_info[0])[0] == exp_id:
                    return exp_id, is_new, expression.get_wt()
            
            
        if not len(self.get_et(operator)):
            self.__et[operator] = dict()
        uid = next(self.__primes_generator)
        wt = 0
        for operand in operands:
            if not isinstance(operand, list) and operand in self.__expressions:# and operand not in self.__st for new_weights
                wt = wt + self.__expressions[operand][0].get_wt()                    
        expression = Expression(uid, operator, operands, uvalue, wt)
        self.__et[operator][uvalue] = (expression, line_no)
        self.__expressions[expression.get_uid()] = (expression, line_no)
        return expression.get_uid(), is_new, expression.get_wt()
    
    
    def process_operands(self, operands, eln):
        operands_uids = []
        n_count = 0 if len(operands)==1 else len(operands)
        is_new = False
        wt = 0
        
        for operand in operands:
            if isinstance(operand, dict):
                uid, is_new, sub_wt = self.process_expression(operand, line_no = eln)
                wt = wt + sub_wt
            
            elif isinstance(operand, tuple):
                uid, who, sub_wt = self.process_member_access(operand, line_no = eln)
                wt = wt + sub_wt
            
            else:
                if isinstance(operand, int):
                    uid, is_new = self.report_symbol(str(operand), ln = eln)
                else:
                    uid, is_new = self.report_symbol("c_"+str(operand), ln = eln)
            
            if is_new and n_count>0:
                n_count = n_count - 1
            operands_uids.append(uid)
        return operands_uids, n_count, wt