import lark as _lark


class ConstantsVisitor(_lark.Visitor):
    def __init__(self):
        self.resolved_constants: dict = {}

    def constants(self, tree: _lark.Tree):
        constants_transformer = ConstantsTransformer()
        visitor = constants_transformer.transform(tree)

        unresolved = {}
        for equation in visitor:
            if equation and "=" in equation:
                key, value = equation.split("=")
                try:
                    evaluated_value = eval(value)
                    self.resolved_constants[key] = evaluated_value
                except NameError:
                    unresolved[key] = value

        while unresolved:
            resolved_this_pass = False
            for key, value in list(unresolved.items()):
                try:
                    evaluated_value = eval(
                        value, {"__builtins__": {}}, self.resolved_constants
                    )
                    self.resolved_constants[key] = evaluated_value
                    del unresolved[key]
                    resolved_this_pass = True
                except NameError:
                    print(f"\nCould not be resolved after pass: {unresolved}")
                    continue

            if not resolved_this_pass and unresolved:
                print(f"\nCould not be resolved: {unresolved}")
                break


class ConstantsTransformer(_lark.Transformer):

    def equation(self, items):
        return f"{items[0]}={items[1]}"

    def explicit_var(self, items):
        return str(items[0])

    def default_visibility_var(self, items):
        # Using lower because the same constant is written in upper and lower in some places
        return str(items[0]).lower()

    def func_call(self, items):
        func_name = items[0]
        args = items[1]
        return f"{func_name}({','.join(args)})"

    def func_name(self, items):
        return items[0]

    def func_args(self, items):
        return items

    def divided_by(self, items):
        return f"{items[0]}/{items[1]}"

    def times(self, items):
        return f"{items[0]}*{items[1]}"

    def to_power_of(self, items):
        return f"{items[0]}**{items[1]}"

    def plus(self, items):
        return f"{items[0]}+{items[1]}"

    def minus(self, items):
        return f"{items[0]}-{items[1]}"

    def negate(self, items):
        return f"-{items[0]}"

    def number(self, items):
        return str(items[0])

    def start(self, items):
        return "\n".join(items)

    def constants(self, items):
        # Skip the "CONSTANTS" token and number_of_constants
        return [x for x in items[2:] if x is not None]
