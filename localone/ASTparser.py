import ast

def parse_flask_routes(file_path):
    """Parse a Flask application to extract route details."""
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    routes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Function Definitions
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', None) == 'route':
                    # Extract route path
                    route_path = decorator.args[0].s
                    # Extract methods
                    methods = []
                    for kw in decorator.keywords:
                        if kw.arg == 'methods' and isinstance(kw.value, ast.List):
                            methods = [elt.s for elt in kw.value.elts]
                    # Collect route details
                    routes.append({
                        'path': route_path,
                        'methods': methods if methods else ['GET'],  # Default to GET
                        'function': node.name,
                        'parameters': [arg.arg for arg in node.args.args if arg.arg != 'self']  # Skip 'self' for methods
                    })
    return routes
