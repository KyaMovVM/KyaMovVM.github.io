import ast
import os
import argparse
from typing import List, Tuple

# type alias for clarity
CrossRef = Tuple[str, str, str, int]

def parse_python_file(path: str) -> List[CrossRef]:
    refs: List[CrossRef] = []
    with open(path, 'r', encoding='utf8') as f:
        source = f.read()
    tree = ast.parse(source, filename=path)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            refs.append(('function', node.name, path, node.lineno))
        elif isinstance(node, ast.ClassDef):
            refs.append(('class', node.name, path, node.lineno))
            for subnode in node.body:
                if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    refs.append(('method', f"{node.name}.{subnode.name}", path, subnode.lineno))
                elif isinstance(subnode, ast.Assign):
                    for target in subnode.targets:
                        name = get_target_name(target)
                        if name:
                            refs.append(('variable', f"{node.name}.{name}", path, subnode.lineno))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                name = get_target_name(target)
                if name:
                    refs.append(('variable', name, path, node.lineno))
    return refs

def get_target_name(target: ast.expr) -> str:
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ''

def collect_refs(root: str) -> List[CrossRef]:
    collected: List[CrossRef] = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith('.py') and fname != os.path.basename(__file__):
                collected.extend(parse_python_file(os.path.join(dirpath, fname)))
    return collected

def main() -> None:
    parser = argparse.ArgumentParser(description='Collect cross references for all methods and variables.')
    parser.add_argument('path', nargs='?', default='.', help='Root path of project')
    parser.add_argument('-o', '--output', help='Output file to write references')
    args = parser.parse_args()

    refs = collect_refs(args.path)
    refs.sort(key=lambda x: (x[1], x[2], x[3]))

    lines = [f"{kind}\t{name}\t{path}:{line}" for kind, name, path, line in refs]
    output = '\n'.join(lines)

    if args.output:
        with open(args.output, 'w', encoding='utf8') as f:
            f.write(output)
    else:
        print(output)

if __name__ == '__main__':
    main()
