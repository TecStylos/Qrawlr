from GrammarRule import ParseData
from GrammarTools import Position
from GrammarParseTree import ParseTree, ParseTreeNode
from GrammarLoader import GrammarLoader
from GrammarException import GrammarException

class ParseResult:
    def __init__(self, tree: ParseTree, farthest_match_position: Position) -> None:
        self.tree = tree
        self.farthest_match_position = farthest_match_position

class Grammar:
    def __init__(self, rules: dict = None, path: str = None, init_tree = None) -> None:
        self.rules = dict()
        
        if rules is not None:
            self.rules = rules
        elif path is not None:
            self.rules = GrammarLoader(path=path).rules
        elif init_tree is not None:
            self.rules = GrammarLoader(init_tree=init_tree).rules

    def apply_to(self, text: str, rule: str, filename: str) -> ParseResult:
        if rule not in self.rules:
            raise GrammarException(f"Rule '{rule}' not found")
        
        parseData = ParseData(text, filename, self.rules)

        tree, _ = parseData.get_rule(rule).match(parseData, 0)

        if tree is not None and isinstance(tree, ParseTreeNode):
            tree.name = rule

        if not parseData.stacks_are_empty():
            raise GrammarException("Stacks not empty after parsing")

        return ParseResult(tree, parseData.get_position(parseData.farthest_match_index))

    def generate_python_code(self, func_name: str = "load_grammar_grammar", add_includes: bool = True) -> str:
        result = ""
        if add_includes:
            result += "from Grammar import Grammar\n"
            result += "from GrammarRule import MatcherInitializers\n"
            result += "from GrammarRule import Rule, MatcherMatchAnyChar\n"
            result += "from GrammarRule import MatcherMatchAll, MatcherMatchAny\n"
            result += "from GrammarRule import MatcherMatchRange, MatcherMatchExact\n"
            result += "from GrammarRule import MatcherMatchRule, MatcherMatchStack\n"

        result += f"def {func_name}() -> Grammar:\n"

        result += "    rules: dict[str, Rule] = {}\n"
        for name, rule in self.rules.items():
            result += f"    rules['{name}'] = {rule._generate_python_code()}\n"

        result += "    return Grammar(rules=rules)\n"

        return result

    def __str__(self) -> str:
        result = ""
        for _, rule in self.rules.items():
            result += f"{rule}\n"
        
        return result
