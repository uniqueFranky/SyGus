from z3 import ModelRef, Int
import translator


class CounterExampleGuider:
    def __init__(self, func_signature, checker, var_decls):
        self.func_define_str = translator.toString(func_signature, ForceBracket=True)
        self.checker = checker
        self.var_decls= var_decls
        self.counter_examples: [ModelRef] = []
        self.ans = None

    def check(self, prog):
        func = self.func_define_str[:-1] + ' ' + translator.toString(prog) + self.func_define_str[-1]
        if not self.test_ces(func):
            return False
        ce = self.checker.check(func)
        if ce is None:
            self.ans = func
            return True
        else:
            if len(ce) > 1:
                self.counter_examples.append(ce)
            return False

    def test_ces(self, func):
        for ce in self.counter_examples:
            self.checker.push()
            for item in ce:
                if item.name() in self.var_decls:
                    var = self.var_decls[item.name()]
                    self.checker.solver.add(var == ce[var])
            counter = self.checker.check(func)
            if counter is not None:
                self.checker.pop()
                return False
            else:
                self.checker.pop()
        return True

    def get_ans(self):
        return self.ans

    def get_counter_examples(self):
        return self.counter_examples
