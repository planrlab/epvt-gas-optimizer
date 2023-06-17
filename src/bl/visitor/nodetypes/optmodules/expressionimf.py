'''
Created on Jan 16, 2021

@author: ACER
'''
from builtins import list

class ExpressionIMF:
    op_pred = {'o++': 10, 'o--': 10, 
               'r++': 20, 'r--': 20, 
               'u-': 21, 
               '!': 22, 
               '~': 23, 
               '**': 30, 
               '*': 40, '/': 40, '%': 40,
               '+': 50, '-': 50, 
               '<<': 60, '>>': 60, 
               '&': 70, 
               '^': 80, 
               '|': 90, 
               '<': 100, '>': 100, '<=': 100, '>=': 100, 
               '==': 110, '!=': 110, 
               '&&': 120, 
               '||': 130, 
               '?': 140
        }
    
    __commutative = ['+', '*'] #, '&&', '||', '&', '|', '!=', '=='
    __associative = ['+', '*'] #, '&&', '||', '!=', '=='
    
     
    @classmethod 
    def update_exp_imf(cls, operator, node_imf):
        if type(node_imf) is dict:
            if operator in node_imf and operator in cls.__commutative and operator in cls.__associative:
                return node_imf.get(operator)
            else:
                return [node_imf]
        else:
            return [node_imf]
            
     
#      
#     def __init__(self, member, l_value = None):
#         self.__operands = []
#         self.__operator = None
#         self.__expression = dict()
#         self.__expr_vc = dict()
#         self.__sub_expressions = self.__set_triplet(member, member.get('name') if member.get('name') else member.get('nodeName'))
#         self.__sign = '+'
#         self.__l_value = l_value.pop() if type(l_value) is set and len(l_value) else str(l_value)
#          
#                  
#     def get_l_value(self):
#         return self.__l_value
#      
#      
#     def __set_triplet(self, exp_member, node_type):
#         print("*****")
#         print(exp_member, node_type, sep = "\n")
#          
#         if node_type == "Conditional":
#             self.__operator = "?"
#          
#         elif node_type == 'UnaryOperation':
#             self.__operator = "u"+exp_member.get('attributes').get('operator')
#          
#         else:
#             self.__operator = exp_member.get('attributes').get('operator')
#          
#         print(self.__operator)
#         #input("555555555555555555")
#          
#         if not self.__operator:
#             if node_type in ['Literal', 'Identifier']:
#                 self.__expression = [exp_member.get('attributes').get('value')]
#             return 
#         else:        
#             self.__expression[self.__operator] = []
#         #print("EXP:", exp_member.get('children'), type(exp_member.get('children')))
#         print(exp_member)
#         for _, member in enumerate(exp_member.get('children')):
#             #print("For--------", self.__operator, self.__expression, sep = "\n")
#             #n_operator = '+'
#             while member.get('name') in ['TupleExpression' ,]:
#                 if member.get('name') == "TupleExpression":
#                     Node.processed.append(member.get('id'))
#                     member = member.get('children')[0]
# #                 else:
# #                     Node.processed.append(member.get('id'))
# #                     n_operator = '-' if member.get('attributes').get('operator') == n_operator else '-'
# #                     member = member.get('children')[0]
# #                     mem_name = member.get('name')
# #                     if mem_name in ['Literal', 'Identifier']:
# #                         actual_value = member.get('attributes').get('value')
# #                         member.get('attributes')['value'] = actual_value if actual_value[0] == n_operator else (n_operator+actual_value[0]) 
# #                     
# #                     elif mem_name == 'TupleExpression':
#              
#             if member.get('name') in ['Literal', 'Identifier']:
#                 operand = member.get('attributes').get('value')
#                 self.__operands.append(operand)
#                 self.__expression[self.__operator].append(operand)
#                 #print(("operator:", self.__operator), self.__expression, sep = "\n")
#             else:
#                 #print(member, type(member))
#                 #input("sub_expr")
#                 sub_expression = Expression(member)
#                 self.__operands.append(sub_expression)
#                  
#                 #print("sub expression", self.__operator, self.__expression, sub_expression.get_expression(), sep = "\n")
#                 expr= sub_expression.get_expression()
#                 if type(expr) is dict: 
#                     for key, value in expr.items():
#                         #print(self.__expression, (key,value), self.__operator, sep = "\n")
#                         if key in self.__expression:
#                             if key == self.__operator:
#                                 if key == "u-":
#                                     self.__expression.pop(key)
#                                     self.__operator = "u+"
#                                     self.__expression[self.__operator] = [value[0]]
#                                      
#                                 elif key in self.__associative:
#                                     self.__expression[key].extend(value)
#                                  
#                                 else:
#                                     self.__expression[key].extend(value)
#                             else:
#                                 operands = self.__expression.get(key)
#                                 #print("Operands:", operands)
#                                 if operands and type(operands[0]) is not list:
#                                     self.__expression[key] = [operands]
#                                 self.__expression[key].append(value)
#                             #input("match?")
#                              
#                         elif key.startswith("u") and self.__operator.startswith("u"):
#                             self.__expression.pop(key)
#                             self.__operator = "u-"
#                             self.__expression[self.__operator] = [value[0]]
#                          
#                         else:
#                             self.__expression[self.__operator].append({key:value})
#                 else:
#                     self.__expression[self.__operator].append(expr)
#                             
#         if self.__operator == "-":
#             print(self.__expression)
#             #input("BFM")
#             self.__operator = '+'
#             value = self.__expression.pop('-')
#              
#             check_operand = value[-1]
#             print(check_operand, self.__expression)
#             count = 0
#             u_ = False
#              
#             while type(check_operand) is dict and ( check_operand.get('u-') or  check_operand.get('u+')):
#                 chk_operand = check_operand.get('u-')
#                 if chk_operand:
#                     count+=1
#                     u_ = True
#                 else:
#                     chk_operand = check_operand.get('u+')
#                  
#                 check_operand = chk_operand
#                      
#                 print(check_operand, count)
#                 #input("c?")
#                  
#                  
#             check_value = check_operand[0] if type(check_operand) is list else check_operand
#             #OTHER CASES NEEDS TO BE HANDLED...............
#              
#             if check_value:
#                 sign = ['', '-']
#                 value.pop(-1)
#                 if not u_:
#                     #Processing - sign to the sub expression
#                     if type(check_value) is dict:
#                         operand = []
#                         t_operator, operands_list = self.process_neg_sign(check_value) 
#                         #t_operator, operand = self.process_neg_sign(member)
# #                         print(t_operator, operands_list)
# #                         input("Wait")
#                         if t_operator == "u+":
#                             operand.append(operands_list)
#                          
#                         elif t_operator != "+":
#                             operand.append({t_operator: operands_list})
#                          
#                         else:
#                             operand.extend(operands_list)  
#                     else: 
#                         operand = self.change_sign(check_value)  
#                 else:
#                     operand = (sign[count%2] + check_value) if '-' == check_value[0] else check_value 
#                  
#                 # To handle '+' after replacement
#                 if len(value) > 0:
#                     if type(value[0]) is dict and '+' in value[0]:
#                         value = value[0].get('+')
#                  
#                 if type(operand) is list:
#                     value.extend(operand)
#                 else:
#                     value.append(operand)
#                  
#             self.__expression[self.__operator] = value 
#          
#         elif self.__operator == "u+":
#             self.__expression = self.__expression.get(self.__operator)[0]
#             #self.__operator = None
#          
#         elif self.__operator == "u-":
#             check_value = self.__expression.get(self.__operator)[0]
#             if type(check_value) is dict:
#                 if list(check_value.keys())[0] not in ['&', '|']:    
#                     t_operator, operands_list = self.process_neg_sign(check_value)
#                     if t_operator == "u+":
#                         self.__expression = operands_list
#                     else:    
#                         self.__expression = {t_operator: operands_list} 
#             else:
#                 self.__expression = self.change_sign(check_value)
#             #self.__operator = None
#        
#     def process_neg_sign(self, expression): 
#         operator = list(expression.keys())[0]
#          
#         if operator in ['&', '|']:
#             return "u-", [expression]
#          
#         elif operator == "u+":
#             return "u-", expression.get("u+")[0]
#           
#         elif operator in ['u-']:
#             #operator = list(expression.get("u-").keys())[0]
#             return "u+", expression.get("u-")[0]
#          
#         operands = expression.pop(operator)
#         if operator in ['+',]:
#             operands_list = []
#             for member in operands:
#                 if type(member) is str:
#                     operands_list.append(self.change_sign(member))
#                 else:
#                     t_operator, operand = self.process_neg_sign(member)
#                     if t_operator == "u+":
#                         operands_list.append(operand)
#                     elif t_operator != "+":
#                         operands_list.append({t_operator: operand})
#                     else:
#                         operands_list.extend(operand)     
#             return operator, operands_list
#              
#         elif operator in ['*',]:
#             operand = None
#             for index, member in enumerate(operands):
#                 if type(member) is str:
#                     #search for -ve operand first
#                     if member.startswith('-'):
#                         operand = index
#                         break
#                     elif not operand:
#                         operand = index
#                      
#             if operand is not None:
#                 operand = operands.pop(index)
#                 operands.insert(index,self.change_sign(operand))
#             else:
#                 operand = operands.pop(0)
#                 t_operator, operand = self.process_neg_sign(member)
#                  
#                 if t_operator == "u+":
#                         operands_list.insert(0, operand)
#                  
#                 elif t_operator != "*":
#                     operands.insert(0,{t_operator: operand})
#                  
#                 else:
#                     operands.extend(operand)
#             return operator, operands
#          
#         else:
#             return operator, operands
#          
#      
#     def change_sign(self, operand):
#         return operand[1:] if operand.startswith('-') else ("-"+operand)        
#      
#      
#     def get_expression(self):
#         return self.__expression