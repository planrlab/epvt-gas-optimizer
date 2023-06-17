'''
Created on June 12, 2023

@author: Arnab Mukherjee
'''
# from src.pl.StaticAnalyzerFramework import StaticAnalyzerFramework
# from time import sleep
import os

# from src.bl.optimizer.OPT__Module import OPTModule


def optimize(source_code: str):
    '''
    Driver method for generating the optimized source code from the EPVT Modules
    '''

    with open('./temp/code.txt', 'w') as f:
        f.write(source_code)

    os.system('python ./api/runner.py')
    
    # saf = StaticAnalyzerFramework()

    # optimized, cse_optimized = saf.analyze_source_code_optimization(source_code)
    
    with open('./temp/opt.txt', 'r') as f:
        optimized = f.read()

    with open('./temp/cse-opt.txt', 'r') as f:
        cse_optimized = f.read()

    return optimized, cse_optimized
