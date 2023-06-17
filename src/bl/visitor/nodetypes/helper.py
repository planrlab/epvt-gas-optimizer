'''
Created on Dec 23, 2020

@author: ACER
'''
  
def get_stmt_declaration(for_src):
        symbol_stack = []
        pos = 0
        for f_c in for_src:
            if f_c == "(":
                symbol_stack.append(f_c)
            elif f_c == ")":
                symbol_stack.pop()
                if len(symbol_stack) == 0:
                    return for_src[1:pos]
            pos +=1
        return for_src[1:pos]


def modify_stmt_children(stmt_children, s_type = None):
    required = ['Block']
    if s_type == "If" and len(stmt_children) == 2:
        required.append("IfStatement")
        #pass
         
    def __modify_stmt(member):
            n_member = dict()
            n_member['id'] = "b_" + str(member.get('id'))
            n_member['name'] = 'Block'
            n_member['src'] = member.get('src')
            n_member['children'] = [member]
            return n_member
        
    for _, child in enumerate(stmt_children):
            #print(child.get('name'))
            if not child.get('name') in required:
                stmt_children.insert(_,__modify_stmt(stmt_children.pop(_)))
   
    return stmt_children