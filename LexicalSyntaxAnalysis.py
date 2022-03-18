import re, os

keyword = ["False", "await", "else", "import", "pass", "None", "break", "except", "in", "raise", "True", "class", "finally", "is", "return", "and", "continue", "for", "lambda", "try", "as", "def", "from", "nonlocal", "while", "assert", "del", "global", "not", "with", "async", "elif", "if", "or", "yield"]
operator = {
    "assign": ["=", "+=", "-=", "*=", "/=", "%=", "//=", "**=", "&=", "|=", "^=", ">>=", "<<="],
    "compare": ["==", "!=", ">", "<", ">=", "<=", "is", "is not"],
    "bool": ["and", "or"],
    "math": ["**", "~", "+", "-", "not", "*", "/", "//", "%", "<<", ">>", "&", "^", "|"]
}
regPattern = {
    "split": r"(\#.*|\[.*?\]|\{.*\}|\".*?\"|\'.*?\'|[a-zA-Z_]+[a-zA-Z_0-9.]*\(|\:|\,|\d+\.{0,1}\d+|[*/<>]{0,1}[+\-*/<>%&|^=!]{0,1}\=|[*/<>]{0,1}[+\-*/<>%&|^~]|>>|<<| is not | is | and | or | not |\w+)",
    "splitImport": r"(from|import)",
    "comment": r"(\#.*)",
    "str": r"(\".*?\"|\'.*?\')",
    "float": r"(\d+\.{1}\d+)",
    "int": r"(\d+)",
    "tuple": r"(^\(.+\)$)",
    "list": r"\[.*\]",
    "dict": r"\{.*\}",
    "fn": r"([a-zA-Z_]+[a-zA-Z_0-9.]*\()",
    "import": r"(^import|^from)",
}

def mergeDict(x: dict, *y: dict) :
    for item in y :
        for key in item :
            x.setdefault(key, [])
            x[key].extend(item[key])
    return x

def split(value: str, isCollection=False) :
    # remove all , in collection
    def mergeCollection(value: list) :
        mc = []
        base = 0
        for i, item in enumerate(value) :
            if item == "," :
                mc.append(value[base:i])
                base = i + 1
        mc.append(value[base:])
        return mc

    # block code
    if isinstance(value, list) :
        return value

    value = value.strip()

    if re.match(regPattern["comment"], value) :
        return [re.sub("'", "\\'", value)]

    if re.match(regPattern["import"], value.strip(), flags=re.M) :
        return [item.strip() for item in re.split(regPattern["splitImport"], value) if item]

    split = re.split(regPattern["split"], value)
    split = [item.strip() for item in split if item and item.strip()]
    merge = []
    base = 0
    for i in range(1, len(split)+1) :
        join = " ".join(split[base:i])
        if re.findall(r"([a-zA-Z_]+[a-zA-Z_0-9.]*\(|\(|\[|\{)", join) :
            dropStr = re.sub(regPattern["str"], "", " ".join(split[base:i]))
            if len(re.findall(r"([a-zA-Z_]+[a-zA-Z_0-9.]*\(|\(|\[|\{)", dropStr)) == len(re.findall(r"(\)|\]|\})", dropStr)) :
                merge.append(join.strip())
                base = i
        else :
            merge.extend(split[base:i])
            base = i
    
    return mergeCollection(merge) if isCollection else merge

def analyzer(value: list) :
    if not value :
        return Blank()
    if len(value) == 1 and not isinstance(value[0], (str, list)):
        return value[0]

    if isinstance(value[0], list) :
        #** : For
        if value[0][0].strip().startswith("for") :
            s = split(value[0][0])
            fi, ii = s.index("for"), s.index("in")
            var = s[fi+1:ii]
        
            return For(analyzer([f"({str.join('', var)})"]) if "," in var else analyzer(var), analyzer(s[ii+1:-1]), [analyzer(split(item)) for item in extractBlock(value[0][1:])])
        #? Check : If-elif-else
        if value[0][0].strip().startswith("if") :
            s = split(value[0][0])
            return If(analyzer(s[1:-1]), [analyzer(split(item)) for item in extractBlock(value[0][1:])], analyzer(value[1:]))
        if value[0][0].strip().startswith("elif") :
            s = split(value[0][0])
            return Elif(analyzer(s[1:-1]), [analyzer(split(item)) for item in extractBlock(value[0][1:])], analyzer(value[1:]))
        if value[0][0].strip().startswith("else") :
            return Else([analyzer(split(item)) for item in extractBlock(value[0][1:])])
    

    #** Assign 
    if any(map(lambda x: x in value, operator["assign"])):
        index = list(map(lambda x: x in operator["assign"], value)).index(True)
        if "," in value[:index] :
            return Assign(analyzer([f"({str.join('', value[:index])})"]), value[index], analyzer([f"({str.join('', value[index+1:])})"]))
        return Assign(analyzer(value[:index]), value[index], analyzer(value[index+1:]))
    #** Operator 
    if any(map(lambda x: x in value, operator["math"])) :
        index = list(map(lambda x: x in operator["math"], value)).index(True)
        index = index + 1 if value[index+1] in operator["math"] else index

        if index == 0 or value[index-1] in operator["math"] :
            return analyzer(value[:index] + [UnaryOperator(value[index], analyzer([value[index+1]]))] + value[index+2:])

        left = list(map(lambda x: x in operator["math"], value[:index])).index(True) if any(map(lambda x: x in value[:index], operator["math"])) else 0
        right = list(map(lambda x: x in operator["math"], value[index+1:])).index(True) if any(map(lambda x: x in value[index+1:], operator["math"])) else len(value[index+1:])
        return analyzer(value[:left] + [Operator(analyzer(value[left:index]), value[index], analyzer(value[index+1:index+1+right]))] + value[index+1+right:])
    #** Compare Op
    if any(map(lambda x: x in value, operator["compare"])) :
        index = list(map(lambda x: x in operator["compare"], value)).index(True)
        allCom = operator["compare"] + operator["bool"]
        left = index - list(map(lambda x: x in allCom, value[:index])).index(True) if any(map(lambda x: x in value[:index], allCom)) else 0
        right = index + 1 + list(map(lambda x: x in allCom, value[index+1:])).index(True) if any(map(lambda x: x in value[index+1:], allCom)) else len(value)        
        return analyzer(value[:left] + [Compare(analyzer(value[left:index]), value[index], analyzer(value[index+1:right]))] + value[right:])
    #** Bool Op (Compare)
    if any(map(lambda x: x in value, operator["bool"])) :
        index = list(map(lambda x: x in operator["bool"], value)).index(True)
        allCom = operator["compare"] + operator["bool"]
        left = index - list(map(lambda x: x in allCom, value[:index])).index(True) if any(map(lambda x: x in value[:index], allCom)) else 0
        right = index + 1 + list(map(lambda x: x in allCom, value[index+1:])).index(True) if any(map(lambda x: x in value[index+1:], allCom)) else len(value)        
        return analyzer(value[:left] + [Compare(analyzer(value[left:index]), value[index], analyzer(value[index+1:right]))] + value[right:])


    #** Comment 
    if re.match(regPattern["comment"], value[0]) :
        return Comment(value[0][value[0].index("#")+1:])
    #** Import
    if re.match(regPattern["import"], value[0], flags=re.M) :
        if value[0] == "import" :
            return Import([Alias(item[0], item[2] if len(item) == 3 else None) for item in split(value[1], isCollection=True)])
        return Module(value[1], analyzer(value[2::]))

    #** Call Function
    if re.match(regPattern["fn"], value[0]): 
        s = [item[:-1] for item in re.split(regPattern["fn"], value[0], maxsplit=1) if item]
        args = split(s[1], isCollection=True)

        # Find index of keyword args
        index = None
        if any(map(lambda x: "=" in x, args)) :
            index = list(map(lambda x: "=" in x, args)).index(True)

        # Connect all attribute and function name
        attr = [Attribute(attr, None) for attr in s[0].split(".")[:-1]] + [Function(s[0].split(".")[-1])]
        for i in range(len(attr)-1) :
            attr[i].func = attr[i+1]
        
        return Call(attr[0], [analyzer(item) for item in args[:index] if item != []], [Keyword(item[0], analyzer([item[2]])) for item in args[index:]] if index != None else [])
    #** Value with Attribute
    if "." in value :
        attr = analyzer([value[2]])
        return Call(Attribute(analyzer([value[0]]), attr.func), attr.args, attr.keyword) if isinstance(attr, Function) else Attribute(analyzer([value[0]]), attr)

    #** Tuple / Parentheses
    if re.match(regPattern["tuple"], value[0], flags=re.M) :
        if "," in split(value[0][1:-1]) :
            if len(value) > 1 :
                return Subscript(analyzer([value[0]]), analyzer([value[1]]) if ":" in value[1] else Index(analyzer([value[1][1:-1]])))
            return Tuple([analyzer(item) for item in split(value[0][1:-1], isCollection=True)])
        return Group(analyzer(split(value[0][1:-1], isCollection=True)[0]))
    #** List / Subscript
    if re.match(regPattern["list"], value[0]) :
        if "," in split(value[0][1:-1]) :
            if len(value) > 1 :
                return Subscript(analyzer([value[0]]), analyzer([value[1]]) if ":" in value[1] else Index(analyzer([value[1][1:-1]])))
            return List([analyzer(item) for item in split(value[0][1:-1], isCollection=True)])
        return Slice(*[analyzer([item]) for item in value[0][1:-1].split(":") + [None, None, None]][0:3])
    #** Dict / Set
    if re.match(regPattern["dict"], value[0]) :
        s = split(value[0][1:-1], isCollection=True)
        if len(s) > 0 and ":" in s[0] :
            if len(value) > 1 :
                return Subscript(analyzer([value[0]]), Index(Constant(value[1][2:-2])))
            return Dict([analyzer(item[:item.index(":")]) for item in s], [analyzer(item[item.index(":")+1:]) for item in s])
        return Set([analyzer(item) for item in s])

    #** Constance Value / Variable
    try :
        if re.match(regPattern["str"], value[0]) :
            if len(value) > 1 :
                return Subscript(analyzer([value[0]]), analyzer([value[1]]) if ":" in value[1] else Index(analyzer([value[1][1:-1]])))
            return Constant(value[0][1:-1])
        if re.match(regPattern["float"], value[0]) :
            return Constant(float(value[0]))
        if re.match(regPattern["int"], value[0]) :
            return Constant(int(value[0]))
        if value[0].isidentifier() and value[0] not in keyword :
            if len(value) > 1 :
                return Subscript(analyzer([value[0]]), analyzer([value[1]]) if ":" in value[1] else Index(analyzer([value[1][1:-1]])))
            return Variable(value[0])
        if value[0] in ["True", "False", "None"] :
            return Constant(eval(value[0]))

    except Exception as e :
        return None

def extractBlock(value: list) :
    spb = ["elif", "else"]
    indent = list(map(lambda x: len(x) - len(x.lstrip()) if len(x.strip()) > 0 else None, value))
    indent = [item if item != None else indent[i-1] for i, item in enumerate(indent)]
    block = []
    base = indent[0]
    index = 0

    while True :
        if any(map(lambda x: x > base, indent[index:])) :
            ist = list(map(lambda x: x > base, indent[index:])).index(True)
            block.extend(value[index:index+ist-1])

            if any(map(lambda x: x == base, indent[index+ist:])) :
                iend = list(map(lambda x: x == base, indent[index+ist:])).index(True)
                b = value[index+ist-1:index+ist+iend]

                if any(map(lambda x: b[0].strip().startswith(x), spb)) :
                    block[-1].append(b)
                else :
                    block.append([b])

                index += ist + iend
            else :
                b = value[index+ist-1:]
                
                if any(map(lambda x: b[0].strip().startswith(x), spb)) :
                    block[-1].append(b)
                else :
                    block.append([b])

                break
        else :
            block.extend(value[index:])
            break

    return block

class Base :
    def __repr__(self) -> str:
        base = "{}={}"
        args = ", ".join([base.format(key, f"'{self.__dict__[key]}'" if isinstance(self.__dict__[key], str) else f"{repr(self.__dict__[key])}") for key in self.__dict__])
        return "{}({})".format(self.__class__.__name__, args)
    
    def __str__(self) -> str:
        return "%s - not imprement __str__" % (self.__class__.__name__)

    def lexical(self) :
        return {}

class Program(Base) :
    def __init__(self, body=[]) -> "Program":
        self.body = body

    def __str__(self) -> str:
        return super().__repr__()

    def readFile(self, filename="") :
        if os.path.exists(filename) :
            with open(filename, "r", encoding="utf-8") as f :
                data = [d.rstrip("\n") for d in f.readlines()]
                return data
        raise FileNotFoundError()

    def analyzer(self, filename="") :
        self.body.clear()
        for line in extractBlock(self.readFile(filename)) :
            a = analyzer(split(line))
            if a :
                self.body.append(a)

    def run(self) :
        exec(self.toCode())

    def toCode(self) -> str:        
        args = self.__dict__
        return " ".join([
            "\n".join(["".join(str(item)) for item in args[name]]) if isinstance(args[name], list) 
            else "".join(str(args[name])) if not isinstance(args[name], (str, int, float)) 
            else str(args[name]) for name in args
        ])

    def toFile(self, path: str) :
        with open(path, "w", encoding="utf-8") as f :
            f.write(self.toCode())

    def getLexical(self) :
        return mergeDict({}, *[item.lexical() for item in self.body])

class Blank(Base) :
    def __str__(self) -> str:
        return ""

class Comment(Base) :
    def __init__(self, value) -> "Comment":
        self.value = value

    def __str__(self) -> str:
        return "#%s" % (str(self.value).replace("\\'", "'"))

    def lexical(self):
        return {"Comment": [self.value[0:10]]}

class Assign(Base) :
    def __init__(self, var, op, value) -> "Assign":
        self.var = var
        self.op = op
        self.value = value

    def __str__(self) -> str:
        return "%s %s %s" % (self.var, self.op, self.value)

    def lexical(self):
        return mergeDict({}, *[self.var.lexical(), {"AssignOperator": [self.op]}, self.value.lexical()])

class Variable(Base) :
    def __init__(self, name) -> "Variable":
        self.name = name

    def __str__(self) -> str:
        return "%s" % (self.name)

    def lexical(self):
        return {"Identifier": [self.name]}

class Constant(Base) :
    def __init__(self, value) -> "Constant":
        self.value = value

    def __str__(self) -> str:
        if isinstance(self.value, str) :
            return "\"%s\"" % (self.value)
        return "%s" % (self.value)

    def lexical(self):
        return {"Value": [self.value]}

class Tuple(Base) :
    def __init__(self, body) -> "Tuple":
        self.body = body

    def __str__(self) -> str:
        return "(%s)" % (", ".join([str(item) for item in self.body]))

    def lexical(self):
        return {"Value": [str(self)]}

class List(Base) :
    def __init__(self, body) -> "List":
        self.body = body

    def __str__(self) -> str:
        return "[%s]" % (", ".join([str(item) for item in self.body]))

    def lexical(self):
        return {"Value": [str(self)]}

class Dict(Base) :
    def __init__(self, key, value) -> "Dict":
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return "{%s}" % (", ".join([f"{key}: {value}" for key, value in zip(self.key, self.value)]))

    def lexical(self):
        return {"Value": [str(self)]}

class Set(Base) :
    def __init__(self, body) -> "Set":
        self.body = body

    def __str__(self) -> str:
        return "{%s}" % (", ".join([str(item) for item in self.body]))

    def lexical(self):
        return {"Value": [str(self)]}

class Subscript(Base) :
    def __init__(self, value, slice) -> "Subscript":
        self.value = value
        self.slice = slice

    def __str__(self) -> str:
        return "%s[%s]" % (self.value, self.slice)
    
    def lexical(self):
        return {"Value": [str(self)]}

class Index(Base) :
    def __init__(self, value) -> "Index":
        self.value = value

    def __str__(self) -> str:
        return "%s" % (self.value)

class Slice(Base) :
    def __init__(self, start, stop, step) -> "Slice":
        self.start = start
        self.stop = stop
        self.step = step

    def __str__(self) -> str:
        return "%s:%s%s" % (self.start if self.start != None else "", self.stop if self.stop != None else "", f":{self.step}" if self.step != None else "")

class Operator(Base) :
    def __init__(self, left, op, right) -> "Operator":
        self.left = left
        self.op = op
        self.right = right
    
    def __str__(self) -> str:
        return "%s %s %s" % (self.left, self.op, self.right)

    def lexical(self):
        return mergeDict({}, *[self.left.lexical(), {"Operator": [self.op]}, self.right.lexical()])

class UnaryOperator(Base) :
    def __init__(self, op, value) -> "UnaryOperator":
        self.op = op
        self.value = value
    
    def __str__(self) -> str:
        return "%s %s" % (self.op, self.value)

    def lexical(self):
        return mergeDict({}, *[{"UnaryOperator": [self.op]}, self.value.lexical()])

class Compare(Base) :
    def __init__(self, left, op, right) -> "Compare":
        self.left = left
        self.op = op
        self.right = right

    def __str__(self) -> str:
        return "%s %s %s" % (self.left, self.op, self.right)

    def lexical(self):
        return mergeDict({}, *[self.left.lexical(), {"CompareOperator": [self.op]}, self.right.lexical()])

class Group(Base) :
    def __init__(self, value) -> "Group":
        self.value = value

    def __str__(self) -> str:
        return "(%s)" % (self.value)

    def lexical(self):
        return self.value.lexical()

class Call(Base) :
    def __init__(self, func, args=[], keyword=[]) -> "Call":
        self.func = func
        self.args = args
        self.keyword = keyword

    def __str__(self) -> str:
        return "%s(%s)" % (self.func, ", ".join([str(item) for item in self.args] + [str(item) for item in self.keyword]), )

    def lexical(self):
        return {"Function": [str(self)]}

class Attribute(Base) :
    def __init__(self, value, func) -> "Attribute":
        self.value = value
        self.func = func

    def __str__(self) -> str:
        return "%s.%s" % (self.value, self.func)

    def lexical(self):
        return {"Value": [str(self)]}

class Function(Base) :
    def __init__(self, name) -> "Function":
        self.name = name

    def __str__(self) -> str:
        return "%s" % (self.name)

class Keyword(Base) :
    def __init__(self, name, value) -> "Keyword":
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return "%s=%s" % (self.name, self.value)

class Module(Base) :
    def __init__(self, name, body) -> "Module":
        self.name = name
        self.body = body

    def __str__(self) -> str:
        return "from %s %s" % (self.name, self.body)

    def lexical(self):
        return mergeDict({"Keyword": ["from"]}, self.body.lexical())

class Import(Base) :
    def __init__(self, name) -> "Import":
        self.name = name

    def __str__(self) -> str:
        return "import %s" % (", ".join([str(item) for item in self.name]))

    def lexical(self):
        return mergeDict({"Keyword": ["import"]}, *[item.lexical() for item in self.name])

class Alias(Base) :
    def __init__(self, name, alias=None) -> "Alias":
        self.name = name
        self.alias = alias

    def __str__(self) -> str:
        return "%s" % (f"{self.name} as {self.alias}" if self.alias != None else self.name)

    def lexical(self):
        return {"Value": [self.name], "Keyword": ["as"] if self.alias else []}

class For(Base) :
    def __init__(self, var, iter, body) -> "For":
        self.var = var
        self.iter = iter
        self.body = body

    def __str__(self) -> str:
        return "for %s in %s :%s" % (self.var, self.iter, "".join([f"\n{item}" for item in self.body]).replace("\n", "\n    "))

    def lexical(self):
        return mergeDict({"Keyword": ["for", "in"]}, *[self.var.lexical(), self.iter.lexical(), *[item.lexical() for item in self.body]])

class If(Base) :
    def __init__(self, condition, body, orelse) -> "If":
        self.condition = condition
        self.body = body
        self.orelse = orelse

    def __str__(self) -> str:
        return "if %s :%s%s" % (self.condition, "".join([f"\n{item}" for item in self.body]).replace("\n", "\n    "), self.orelse)

    def lexical(self):
        return mergeDict({"Keyword": ["if"]}, *[self.condition.lexical(), *[item.lexical() for item in self.body], self.orelse.lexical()])

class Elif(If) :
    def __str__(self) -> str:
        return "\nelif %s :%s%s" % (self.condition, "".join([f"\n{item}" for item in self.body]).replace("\n", "\n    "), self.orelse)

    def lexical(self):
        return mergeDict({"Keyword": ["elif"]}, *[self.condition.lexical(), *[item.lexical() for item in self.body], self.orelse.lexical()])

class Else(Base) :
    def __init__(self, body) -> "Else":
        self.body = body

    def __str__(self) -> str:
        return "\nelse :%s" % ("".join([f"\n{item}" for item in self.body]).replace("\n", "\n    "))
    
    def lexical(self):
        return mergeDict({"Keyword": ["else"]}, *[item.lexical() for item in self.body])