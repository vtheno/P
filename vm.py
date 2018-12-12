#coding=utf-8
from util import Stack

class Instruction(type): 
    def __new__(cls, name, bases, attrs, **kws):
        attrs["__name__"] = name
        attrs["__repr__"] = lambda self: self.__name__
        return type.__new__(cls, name, bases, attrs)()
class Load(metaclass=Instruction): pass
class Save(metaclass=Instruction): pass
class Add(metaclass=Instruction): pass
class Assgin(metaclass=Instruction): pass
class Jump(metaclass=Instruction): pass
class JumpOnTrue(metaclass=Instruction): pass
class JumpOnFalse(metaclass=Instruction): pass
class Call(metaclass=Instruction): pass
class Execute(metaclass=Instruction): pass

class Machine(object):
    def __init__(self):
        self.stack = Stack()
        self.program_count = 0
        self.compare_flag = False
        """
        self.memory = [None] * (256 ** 3)
        self.ptr = 0
    def malloc(self):
        pass
    def free(self):
        pass
        """
    def __repr__(self):
        return f"cmp flag: {self.compare_flag}  pc: {self.program_count}  stack: {self.stack}"
    def run(self, insts: [(Instruction,...)]):
        _len = len(insts)
        self.program_count = 0
        self.compare_flag = False
        while self.program_count < _len:
            current_instruction = inst[self.program_count]
            self.program_count += 1
m = Machine()
print( m )
"""
let x = 1 
in x

;; CONST 1 ;; how load to ?
;; STORE 0
;; 
"""
