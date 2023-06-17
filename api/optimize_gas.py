'''
Created on June 12, 2023

@author: Arnab Mukherjee
'''
from src.pl.StaticAnalyzerFramework import StaticAnalyzerFramework
from time import sleep

# from src.bl.optimizer.OPT__Module import OPTModule


def optimize(source_code: str):
    '''
    Driver method for generating the optimized source code from the EPVT Modules
    '''
    
    saf = StaticAnalyzerFramework()

    optimized, cse_optimized = saf.analyze_source_code_optimization(source_code)
    

    return optimized, cse_optimized
