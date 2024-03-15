import sys
import sexp
import pprint
import translator


def Extend(Stmts, Productions):
    ret = []
    for i in range(len(Stmts)):
        if type(Stmts[i]) == list:
            TryExtend = Extend(Stmts[i], Productions)
            if len(TryExtend) > 0:
                for extended in TryExtend:
                    ret.append(Stmts[0:i] + [extended] + Stmts[i + 1:])
        elif Stmts[i] in Productions:
            for extended in Productions[Stmts[i]]:
                ret.append(Stmts[0:i] + [extended] + Stmts[i + 1:])
    return ret


def stripComments(bmFile):
    noComments = '('
    for line in bmFile:
        line = line.split(';', 1)[0]
        noComments += line
    return noComments + ')'


if __name__ == '__main__':
    benchmarkFile = open(sys.argv[1])
    bm = stripComments(benchmarkFile)
    bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0]  # Parse string to python list
    checker = translator.ReadQuery(bmExpr)
    SynFunExpr = []
    StartSym = 'My-Start-Symbol'  # virtual starting symbol
    for expr in bmExpr:
        if len(expr) == 0:
            continue
        elif expr[0] == 'synth-fun':
            SynFunExpr = expr
    FuncDefine = ['define-fun'] + SynFunExpr[1:4]  # copy function signature
    BfsQueue = [[StartSym]]  # Top-down
    Productions = {StartSym: []}
    Type = {StartSym: SynFunExpr[3]}  # set starting symbol's return type

    for NonTerm in SynFunExpr[4]:  # SynFunExpr[4] is the production rules
        NTName = NonTerm[0]
        NTType = NonTerm[1]
        if NTType == Type[StartSym]:
            Productions[StartSym].append(NTName)
        Type[NTName] = NTType
        Productions[NTName] = []
        for NT in NonTerm[2]:
            if type(NT) == tuple:
                Productions[NTName].append(str(NT[1]))  # deal with ('Int',0). You can also utilize type information,
                # but you will suffer from these tuples.
            else:
                Productions[NTName].append(NT)
    Count = 0
    while len(BfsQueue) != 0:
        Curr = BfsQueue.pop(0)
        TryExtend = Extend(Curr, Productions)
        if len(TryExtend) == 0:  # Nothing to extend
            FuncDefineStr = translator.toString(FuncDefine, ForceBracket=True)  # use Force Bracket = True on
            # function definition. MAGIC CODE. DO NOT MODIFY THE ARGUMENT ForceBracket = True.
            CurrStr = translator.toString(Curr)

            Str = FuncDefineStr[:-1] + ' ' + CurrStr + FuncDefineStr[
                -1]  # insert Program just before the last bracket ')'
            Count += 1
            counterexample = checker.check(Str)
            if counterexample == None:  # No counter-example
                Ans = Str
                break

        TE_set = set()
        for TE in TryExtend:
            TE_str = str(TE)
            if not TE_str in TE_set:
                BfsQueue.append(TE)
                TE_set.add(TE_str)

    print(Ans)
