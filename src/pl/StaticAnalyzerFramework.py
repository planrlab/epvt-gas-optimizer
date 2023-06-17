'''
Created on Feb 3, 2022

@author: JH-ANIC
'''
import os, sys


from src.bl.compiler.output_generator import CompiledOutputGenerator
from src.bl.compiler.solc_selector import SolcSelector
from src.bl.visitor.ast_reader import ASTToCFGObject
# from src.bl.sagt.ssa_v1 import SAGGenerator
from src.bl.optimizer.OPT__Module import OPTModule
#from src.bl.sagt.ssa_old import SAGGenerator
import solcx
# from memory_profiler import memory_usage, profile
# import cProfile, pstats, io


class StaticAnalyzerFramework(object):
    # ms = open("A:\\workspace\\eclipse-workspace\\EPVT_approach_2\\src\\pl/ms.log", "w+")
    def __init__(self, file_path = None, file_name = None, _s_type = None, _cfg_format = "pdf", _version = "0.5.9", _cfg_output_file = "cfg_file"):
        self.solidity_compiler_version = _version
        self.cfg_format = _cfg_format
        self.cfg_output_file = _cfg_output_file
        self.code_statistics = None
        # sag_generator = self.__analyze_single_file(file_path+file_name+".sol")
        # self.result = sag_generator.generate_sag_forms(file_name, _s_type)
#         input("AKKKKKKKKKKKKKKKKKKKKKK")
    
    # def get_result(self):
    #     return self.result
    
#     @profile(stream=ms, precision=4)
#     def analyze_source_code_file(self, source_code):
#         solidity_pragma = self.__extract_solidity_version(source_code)
#         if not solidity_pragma:
#             solidity_version = self.solidity_compiler_version
#         else:
#             solidity_version = SolcSelector.install_solc_pragma_solc(self, solidity_pragma)
        
#         self.__initialize_solidity_compiler(solidity_version)  
        
#         helper = CompiledOutputGenerator(source_code)
#         ast_to_cfg_obj = self.get_OGR(source_code, helper) 
#         # self.__cfg_object = ast_to_cfg_obj.get_cfg_object()
#         # builder = ast_to_cfg_obj.get_cfg_builder()
#         # self.code_statistics = ast_to_cfg_obj.get_code_statistics()
        
#         # builder.draw_cfg(self.__cfg_object.get_dgraph(), path = self.cfg_output_file+self.cfg_format, cfg_format = self.cfg_format, file_name = self.cfg_output_file)
        
#         self.opt_module = OPTModule(self.get_cfg_object())
#         opt_source_code = self.opt_module.get_optimized_code(source_code)    
#         opt_cse_source_code = self.opt_module.get_optimized_code(source_code, True)

# #         print("Contracts:", self.__cfg_object.get_contracts())
# #         print("Functions:", self.__cfg_object.get_contracts()[0].get_functions()) 
# #         print("Statistics:\n\n", self.code_statistics)
# #         input("Check CNTS")
#         del helper
#         del ast_to_cfg_obj
#         # return self.get_SAG()
#         return opt_source_code, opt_cse_source_code

    def analyze_source_code_optimization(self, source_code: str) -> str:
        solidity_pragma = self.__extract_solidity_version(source_code)
        if not solidity_pragma:
            solidity_version = self.solidity_compiler_version
        else:
            solidity_version = SolcSelector.install_solc_pragma_solc(
                self, solidity_pragma)

        self.__initialize_solidity_compiler(solidity_version)

        helper = CompiledOutputGenerator(source_code)
        ast_to_cfg_obj = ASTToCFGObject(source_code, helper.get_ast())
        self.__cfg_object = ast_to_cfg_obj.get_cfg_object()

        self.opt_module = OPTModule(self.__cfg_object)
        opt_source_code = self.opt_module.get_optimized_code(source_code)
        opt_cse_source_code = self.opt_module.get_optimized_code(
            source_code, True)

        return opt_source_code, opt_cse_source_code    
        
    # @profile
    def get_OGR(self, source_code, helper):
        return ASTToCFGObject(source_code, helper.get_ast()) 
    
    # @profile
    # def get_SAG(self):
    #     return SAGGenerator(self.__cfg_object)
       
       
    # def __analyze_single_file(self, file_path):
    #     source_code = self.__extract_source_code(file_path)
    #     # return self.analyze_source_code_file(source_code)
        
    # @profile    
    def __initialize_solidity_compiler(self, solc_version):
        solidity_compiler_version= solc_version
        if solidity_compiler_version.startswith("v0"):
            if solidity_compiler_version not in solcx.get_installed_solc_versions():
                # msg = "Wait a while downloading Solidity compiler"
                try:
                    solcx.install_solc(solc_version)
                except Exception as e:
                    sys.stderr.write("Error while downloading required Solidity compiler "+ str(solidity_compiler_version) + str(e))
                    sys.stderr.write("Check with different Solidity compiler version" + str(e))
                    return None
            solcx.set_solc_version(solidity_compiler_version)
        
    
    # def __extract_source_code(self, file_name:str):
    #     if file_name.startswith("."):
    #         file_name = os.path.join(os.getcwd(), file_name)
    #     with open(file_name) as fd:
    #         source_code = fd.read()
    #     return source_code
    
    
    def __extract_solidity_version(self, source_code):
        """extract solidity version based on pragma"""
        for line_text in source_code.split('\n'):
            if line_text.startswith('pragma solidity'):
                return line_text
        return None


# if __name__ == "__main__":
#     from prettytable import PrettyTable
#     import csv
#     from collections import OrderedDict
    
#     tests_files = 10
    
#     table_hdr = ['SAG_TYPE', 'Sr No.', 'FileName', '#Contracts', '#Functions', 'FunctionID', '#Variables', '#Overhead', "#Dead_nodes", "EN","EX","RC","CV","SPV","NP","Time","OGR Size", "SA OBJ Size"]
#     results = PrettyTable(table_hdr)
# #     test_files = ["test", "test1", "test2","test3","test4"]
# #     test_files = ["test1","test3"]
#     sag_types = ["ssa"]
    

#     output = open('A:\\workspace\\eclipse-workspace\\EPVT_approach_2\\src\\pl\\output.csv', 'w+', newline='')
#     fieldnames = []
#     file_statistics = []
    
#     for sr_no, file_name in enumerate(range(25,26)):
#         saf = None
#         for sag_type in sag_types:
# #             pr = cProfile.Profile()
# #             pr.enable()
# #             # ... do something ...
#             saf = StaticAnalyzerFramework("A:\\workspace\\eclipse-workspace\\EPVT_approach_2\\src\\pl/examples/", "t"+str(file_name), sag_type)
            
#             for i, result in enumerate(saf.get_result()):
#                 row = list(result.values())
#                 if i == 0:
#                     row.insert(0, sr_no + 1)
#                 else:
#                     row.insert(0, '_')
#                 row.insert(0, sag_type)
#                 results.add_row(row)
                
#         saf.code_statistics['file_name'] = "t"+str(file_name)
#         fieldnames.extend(saf.code_statistics.keys())
#         file_statistics.append(saf.code_statistics)
#         del saf
        
    
#     print(results)
#     results.border = False         
    
#     for i, fs in enumerate(file_statistics):
#         for k in set(fieldnames):
#             if k not in fs:
#                 fs[k] = ""
        
#         fs = OrderedDict(sorted(fs.items()))
#         if i == 0:
#             writer = csv.DictWriter(output, fieldnames=fs.keys())
#             writer.writeheader()
#         writer.writerow(fs) 
#     output.close()
#     with open('A:\\workspace\\eclipse-workspace\\EPVT_approach_2\\src\\pl\\/ssa.csv','a+', newline='') as f:
#         f.write(results.get_csv_string())
#         f.close

# #     
    
            