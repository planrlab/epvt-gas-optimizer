from src.pl.StaticAnalyzerFramework import StaticAnalyzerFramework

with open('./temp/code.txt', 'r') as f:
    source_code = f.read()

saf = StaticAnalyzerFramework()

optimized, cse_optimized = saf.analyze_source_code_optimization(source_code)

with open('./temp/opt.txt', 'w') as f:
    f.write(optimized)

with open('./temp/cse-opt.txt', 'w') as f:
    f.write(cse_optimized)
