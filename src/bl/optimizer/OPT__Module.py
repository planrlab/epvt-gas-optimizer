'''
Created on Mar 3, 2021

@author: ACER
'''
from src.bl.optimizer.BlockSTET import BlockSTET


class OPTModule(object):
    exclude_var = dict()
    optimized_expressions = []
    optimized_expressions_bs = []
    is_back_substitution_possible = False
    
    def __init__(self, _cfg):
        self._cfg = _cfg
        self._seq_no = 0
        self._diff = 0
        self.prev_oe_len = 0
        BlockSTET.set_tokens(_cfg.get_token_info())
        '''
        #
        # OPTIMIZATION
        #
        '''
        self.optimize()
    
    
    def get_unreachable_code(self):
        return self.__unreachable_nodes
    
    
    def get_opt_source_code(self):
        return self.__opt_source_code
    
    
    def update_exclude_var(self, defined_list, insert_new = True):
        if insert_new:
            for var in set(defined_list):
                self.exclude_var[var] = 1 if var not in self.exclude_var else self.exclude_var[var] + 1
        else:
            for var in set(defined_list):
                if var not in self.exclude_var:
                    raise("Error Trying to exclude variable which is not in the Scope")
                else:
                    self.exclude_var[var] = self.exclude_var[var] - 1
                    if self.exclude_var[var] == 0:
                        self.exclude_var.pop(var)
                        
    
    def update_current_scope(self, defined_list):
        pass
    
    
    def auto_optimize(self):
        pass
    
    
    def contains_skipped(self, l1, node):
        return list(set(l1) & set(node.get_used()))
    
    
    def remove_from_skiped(self, l1, node):
        return True if len(list(set(l1) & set(node.get_used()))) > 0 else False
     
    
    def startsWithAny(self, name, checkList):
        if type(name) is str:
            for x in checkList:
                if name.startswith(x):
                    return True
        return False
            
    
    def record_optimized_expressions_bs(self, opt_expressions):
        if opt_expressions:
            self.is_back_substitution_possible = True
            diff_len = len(self.optimized_expressions_bs) + len(opt_expressions) - len(self.optimized_expressions) - self._diff
            self._diff += diff_len
            cpos = len(self.optimized_expressions) - len(opt_expressions) + diff_len
            start =  self.optimized_expressions[-1*(len(opt_expressions) - diff_len)][0][0]
            for pos, exp in enumerate(opt_expressions):
                if pos<diff_len:
                    if isinstance(exp, tuple):
                        self.optimized_expressions_bs.append(((exp[0][0],0), exp[1], None))
                    else:
                        self.optimized_expressions_bs.append(((start,0), exp, None))
                else:
                    self.optimized_expressions_bs.append((self.optimized_expressions[cpos][0], exp, self.optimized_expressions[cpos][2]))
                    cpos += 1
        else:
            self.optimized_expressions_bs.extend(self.optimized_expressions[self.prev_oe_len:])
        self.prev_oe_len = len(self.optimized_expressions)
        self.optimized_expressions_bs.sort(key = lambda x: x[0][0])
        
    
    def satisfy_unlock(self, _node):
        if _node and _node.get_previous_nodes():
            if not isinstance(_node.get_previous_nodes(), list):
                return True
            for node in _node.get_previous_nodes():
                if node.get_visit_count() == 0 and not node.get_is_unreachable():
                    return False
            return True
        else:
            return False
        
    def optimize(self):
        #scopes = []
        curr_scope = None
        contract_scope = None
        #f_b = BlockSTET(c_b)
        _source_node = self._cfg
        n_visited = [(_node, None) for _node in _source_node.get_contracts()]
        while (len(n_visited) > 0):             
            next_nodes = None
            next_node = n_visited.pop(0)
            _node = next_node[0]
            
            if next_node[1]:
                curr_scope = next_node[1]
                
            _node.update_visit_count(1)
            cfg_id = _node.get_cfg_id()
            vc = _node.get_visit_count()
            nn_condition = False
            if vc == 1:
                if isinstance(cfg_id, str):
                    if cfg_id == "Contract":
                        contract_scope = BlockSTET()
                        curr_scope = contract_scope
                        nn_condition = True
                        
                    elif cfg_id.startswith("START_"):
                        contract_scope = curr_scope
                        nn_condition = True
                        if curr_scope:
                            curr_scope = BlockSTET(curr_scope)
                        else:
                            raise("Error")
                        
                    elif cfg_id.startswith("STOP_") and self.satisfy_unlock(_node):
                        opt_expressions = curr_scope.optimize_available_expressions()
                        self.record_optimized_expressions_bs(opt_expressions)
                        curr_scope = contract_scope
                        curr_scope.init_backsubstitution()
                        
                        
                    elif self.startsWithAny(cfg_id, ["CN_F", "CN_W", "EN_DW"]):
                        _node.get_opp_node().set_previous_skip(curr_scope.get_skip())
                        if self.satisfy_unlock(_node):
                            _node.get_opp_node().set_reset()
                        else:
                            curr_scope.set_skip(_node.get_used_def())
                        nn_condition = True
                    
                    elif cfg_id.startswith("stop") and self.satisfy_unlock(_node):
                        contract_scope = BlockSTET(curr_scope)
                    
            
            t_condi = True
            if self.startsWithAny(cfg_id, ["JN_F", "JN_IF", "JN_W", "JN_DW"]):
                if self.satisfy_unlock(_node):
                    if not cfg_id.startswith("JN_IF"):
                        if not self.satisfy_unlock(_node.get_opp_node()):
                            n_visited.insert(1, next_node)
                            t_condi =False
                    if t_condi:        
                        self._seq_no += 1
                        if _node.get_reset():
                            curr_scope.re_assign_uids(_node.get_dec_def(), self._seq_no)
                        curr_scope.set_skip(_node.get_previous_skip())        
                
            imf = _node.get_imf()
            if imf:
                self._seq_no += 1
                skip_set = curr_scope.get_skip()
                skipped_list = self.contains_skipped(skip_set, _node)
                curr_scope.re_assign_uids(skipped_list, self._seq_no)
                curr_scope.set_location_info(_node.get_src_indices())
                curr_scope.process_expression(imf, self._seq_no, sub_exp = False)

                if skip_set and len(skip_set) > 0:
                    curr_scope.modify_scope(_node, self._seq_no)
                    
                if curr_scope.optimized_expression: #skipping Extra Nodes of CFG
                    self.optimized_expressions.append((_node.get_src_indices(), curr_scope.optimized_expression, _node.get_data_type()))
                    curr_scope.reset()
                                
            if t_condi and (nn_condition or (self.satisfy_unlock(_node) and not _node.get_visited())):
                next_nodes = _node.get_next_nodes()
                _node.set_visited()
                if type(next_nodes) is list:
                    n_visited[0:0] = [(next_node, BlockSTET(curr_scope) if _node.get_name()!="DWL_C" else None) for next_node in next_nodes]
                elif next_nodes:
                    n_visited.insert(0, (next_nodes, None))
            else:
                next_nodes = _node.get_next_nodes()
             
    
    def __generate_optimized_code(self, src_code, is_back_substitution_enabled = False):
        relative_count = 0
        if is_back_substitution_enabled and self.is_back_substitution_possible:
            is_back_substitution_enabled = True
        else:
            is_back_substitution_enabled = False
        expressions = self.optimized_expressions_bs if is_back_substitution_enabled else self.optimized_expressions
        for exp in expressions:
            org_pos, code, data_type = exp
            pos = 0
            if isinstance(org_pos, tuple) and org_pos[1]!=0:
                s, e = org_pos[0]+relative_count, sum(org_pos)+relative_count
                if not data_type:
                    data_type = ""
                else:
                    data_type += " "
                opt_snippet = data_type + code
                
                org_snippet = src_code[s:e]
                relative_count += len(opt_snippet) - len(org_snippet)
            else:
                org_pos = org_pos[0]
                pos = 1
                s = src_code[:org_pos+relative_count].rfind(";")
                if s == -1:
                    s = org_pos   
                e = s+pos
                opt_snippet = "\n/* CSE */\t"+code + ";"
                relative_count += len(opt_snippet)
            src_code = src_code[:s+pos] + opt_snippet + src_code[e:]                   
        return src_code
            
            
    def get_optimized_code(self, src, is_back_sub = False): 
        return self.__generate_optimized_code(src, is_back_sub)
    
    