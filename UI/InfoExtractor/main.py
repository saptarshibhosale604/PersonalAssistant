#!/usr/bin/env python3
"""
function_scanner.py
====================

Scans a Python project directory and produces a full inventory of every
function it finds: file name, function name, parameters, argument
defaults, docstring description, and its dependencies (both calls to
other functions in the project, and calls into external libraries).

Output:
    <outdir>/functions_report.json   - structured data, one entry per function
    <outdir>/functions_report.md     - human-readable Markdown report
    <outdir>/dependency_graph.html   - interactive graph (pyvis, zoom/drag/hover)
    <outdir>/dependency_graph.png    - static image of the same graph

Usage:
    python function_scanner.py /path/to/project
    python function_scanner.py /path/to/project --outdir ./scan_output
    python function_scanner.py /path/to/project --exclude venv,.git,build

Notes on how call resolution works (heuristic, not a type checker):
    - `foo()`               -> looked up by name against every function
                                 found in the project. If found, an edge
                                 is drawn function -> foo.
    - `self.bar()` / `cls.bar()`
                             -> looked up by name against methods defined
                                 in the *same class*.
    - `module.func()`       -> the leading name is checked against this
                                 file's import table. If it resolves to an
                                 imported module/package, it's recorded as
                                 an *external* dependency (e.g. "os.path.join").
    - anything else (calls on arbitrary objects/instances, results of
      other calls, etc.) is recorded in the function's raw call list but
      is not turned into a graph edge, since we can't know its type
      without running the code.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import networkx as nx

DEFAULT_EXCLUDES = {
    ".git", "__pycache__", "venv", ".venv", "env", "build", "dist",
    "node_modules", ".mypy_cache", ".pytest_cache", "site-packages",
}


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class FunctionInfo:
    file_name: str                     # relative path of the source file
    function_name: str                 # def name
    class_name: str | None             # enclosing class, if it's a method
    qualified_name: str                # "Class.method" or just "function"
    node_id: str                       # unique graph node id: "file::qualified_name"
    line_number: int
    parameters: list[dict]             # [{"name": ..., "annotation": ...}, ...]
    arguments: dict[str, str]          # default values, keyed by parameter name
    description: str                   # docstring, verbatim
    dependencies: list[dict]           # resolved deps: [{"target": ..., "type": "internal"|"external"}]
    raw_calls: list[str]               # every call expression seen, unresolved or not


# --------------------------------------------------------------------------
# AST helpers
# --------------------------------------------------------------------------

def _unparse(node) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def extract_parameters(args: ast.arguments) -> tuple[list[dict], dict[str, str]]:
    """Return (parameter list, {param_name: default_expression}) for a function signature."""
    params: list[dict] = []
    defaults: dict[str, str] = {}

    all_positional = list(args.posonlyargs) + list(args.args)
    # positional defaults align to the *end* of the positional arg list
    pos_defaults = list(args.defaults)
    offset = len(all_positional) - len(pos_defaults)
    for i, a in enumerate(all_positional):
        params.append({"name": a.arg, "annotation": _unparse(a.annotation)})
        if i >= offset:
            defaults[a.arg] = _unparse(pos_defaults[i - offset])

    if args.vararg:
        params.append({"name": f"*{args.vararg.arg}", "annotation": _unparse(args.vararg.annotation)})

    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        params.append({"name": a.arg, "annotation": _unparse(a.annotation)})
        if d is not None:
            defaults[a.arg] = _unparse(d)

    if args.kwarg:
        params.append({"name": f"**{args.kwarg.arg}", "annotation": _unparse(args.kwarg.annotation)})

    return params, defaults


def collect_import_table(tree: ast.Module) -> dict[str, str]:
    """Map local alias -> real dotted module name, for top-level imports in a file."""
    table: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                table[local] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                local = alias.asname or alias.name
                table[local] = f"{node.module}.{alias.name}"
    return table


def collect_calls_in_function(func_node) -> list[ast.Call]:
    """Every ast.Call directly inside this function, NOT descending into nested
    function/lambda definitions (those are collected as their own entries)."""
    calls: list[ast.Call] = []

    def walk(n):
        for child in ast.iter_child_nodes(n):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(child, ast.Call):
                calls.append(child)
            walk(child)

    walk(func_node)
    return calls


def call_target_name(call: ast.Call) -> str | None:
    """Best-effort dotted name for what's being called, e.g. 'foo', 'self.bar', 'os.path.join'."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        cur = func.value
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        parts.reverse()
        return ".".join(parts)
    return None


# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------

class ProjectScanner:
    def __init__(self, root: Path, excludes: set[str]):
        self.root = root
        self.excludes = excludes
        self.functions: list[FunctionInfo] = []
        # for resolving "self.method()" calls: {class_name: {method_name: node_id}}
        self._methods_by_class: dict[str, dict[str, str]] = {}
        # for resolving plain "foo()" calls: {function_name: [node_id, ...]}
        self._functions_by_name: dict[str, list[str]] = {}

    def find_python_files(self) -> list[Path]:
        files = []
        for path in self.root.rglob("*.py"):
            if any(part in self.excludes for part in path.parts):
                continue
            files.append(path)
        return sorted(files)

    def scan(self):
        files = self.find_python_files()
        # Pass 1: parse every file, record every function's identity + signature.
        parsed: list[tuple[Path, ast.Module, dict[str, str]]] = []
        pending: list[tuple] = []  # (file, rel, class_name, node)

        for path in files:
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"  [skip] {path}: {e}", file=sys.stderr)
                continue

            rel = str(path.relative_to(self.root))
            imports = collect_import_table(tree)
            parsed.append((path, tree, imports))

            class_stack: list[str] = []

            class Visitor(ast.NodeVisitor):
                def visit_ClassDef(self, node):
                    class_stack.append(node.name)
                    self.generic_visit(node)
                    class_stack.pop()

                def visit_FunctionDef(self, node):
                    self._record(node)
                    self.generic_visit(node)

                def visit_AsyncFunctionDef(self, node):
                    self._record(node)
                    self.generic_visit(node)

                def _record(vself, node):
                    class_name = class_stack[-1] if class_stack else None
                    qualified = f"{class_name}.{node.name}" if class_name else node.name
                    node_id = f"{rel}::{qualified}"
                    pending.append((path, rel, class_name, qualified, node_id, node))

            Visitor().visit(tree)

        # Build lookup tables before resolving dependencies.
        for _, rel, class_name, qualified, node_id, node in pending:
            self._functions_by_name.setdefault(node.name, []).append(node_id)
            if class_name:
                self._methods_by_class.setdefault(class_name, {})[node.name] = node_id

        # Pass 2: extract full info + resolve dependencies now that lookups exist.
        imports_by_path = {str(p): imports for p, _, imports in parsed}

        for path, rel, class_name, qualified, node_id, node in pending:
            params, defaults = extract_parameters(node.args)
            description = ast.get_docstring(node) or ""
            imports = imports_by_path.get(str(path), {})

            calls = collect_calls_in_function(node)
            dependencies = []
            raw_calls = []
            for call in calls:
                name = call_target_name(call)
                if name is None:
                    continue
                raw_calls.append(name)
                dependencies.append(self._resolve(name, class_name, imports))

            self.functions.append(FunctionInfo(
                file_name=rel,
                function_name=node.name,
                class_name=class_name,
                qualified_name=qualified,
                node_id=node_id,
                line_number=node.lineno,
                parameters=params,
                arguments=defaults,
                description=description,
                dependencies=[d for d in dependencies if d is not None],
                raw_calls=raw_calls,
            ))

    def _resolve(self, name: str, class_name: str | None, imports: dict[str, str]) -> dict | None:
        # self.method() / cls.method() -> internal, same class
        if "." in name:
            root, _, rest = name.partition(".")
            if root in ("self", "cls") and class_name:
                target = self._methods_by_class.get(class_name, {}).get(rest.split(".")[0])
                if target:
                    return {"target": target, "type": "internal"}
                return None
            if root in imports:
                resolved_module = imports[root]
                return {"target": f"{resolved_module}.{rest}" if rest else resolved_module, "type": "external"}
            # unresolved attribute call (e.g. some_instance.method()) - skip edge
            return None

        # plain name() call
        if name in self._functions_by_name:
            candidates = self._functions_by_name[name]
            # if ambiguous (same function name defined in multiple files), link to all
            if len(candidates) == 1:
                return {"target": candidates[0], "type": "internal"}
            return {"target": candidates, "type": "internal-ambiguous"}

        if name in imports:
            return {"target": imports[name], "type": "external"}

        if name in dir(__builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)):
            return {"target": name, "type": "builtin"}

        return {"target": name, "type": "unresolved"}


# --------------------------------------------------------------------------
# Export: JSON + Markdown
# --------------------------------------------------------------------------

def export_json(functions: list[FunctionInfo], outpath: Path):
    data = [asdict(f) for f in functions]
    outpath.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_markdown(functions: list[FunctionInfo], outpath: Path):
    lines = ["# Function report", ""]
    by_file: dict[str, list[FunctionInfo]] = {}
    for f in functions:
        by_file.setdefault(f.file_name, []).append(f)

    for file_name in sorted(by_file):
        lines.append(f"## `{file_name}`")
        lines.append("")
        for f in sorted(by_file[file_name], key=lambda x: x.line_number):
            lines.append(f"### `{f.qualified_name}` (line {f.line_number})")
            if f.description:
                lines.append(f"> {f.description.strip().splitlines()[0]}")
            lines.append("")
            param_str = ", ".join(
                p["name"] + (f": {p['annotation']}" if p["annotation"] else "") for p in f.parameters
            ) or "(none)"
            lines.append(f"- **Parameters:** {param_str}")
            arg_str = ", ".join(f"{k}={v}" for k, v in f.arguments.items()) or "(none)"
            lines.append(f"- **Default arguments:** {arg_str}")
            if f.dependencies:
                dep_str = ", ".join(
                    (d["target"] if isinstance(d["target"], str) else "/".join(d["target"]))
                    + f" [{d['type']}]" for d in f.dependencies
                )
                lines.append(f"- **Dependencies:** {dep_str}")
            else:
                lines.append("- **Dependencies:** (none detected)")
            lines.append("")
    outpath.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------
# Graph building + visualization
# --------------------------------------------------------------------------

def build_graph(functions: list[FunctionInfo]) -> nx.DiGraph:
    g = nx.DiGraph()
    for f in functions:
        g.add_node(f.node_id, label=f.qualified_name, file=f.file_name,
                    kind="function", title=f.description or f.qualified_name)

    for f in functions:
        for dep in f.dependencies:
            target = dep["target"]
            dtype = dep["type"]
            if dtype == "internal-ambiguous":
                for t in target:
                    g.add_edge(f.node_id, t, kind=dtype)
                continue
            if dtype == "internal":
                g.add_edge(f.node_id, target, kind=dtype)
            elif dtype == "external":
                ext_id = f"ext::{target}"
                if ext_id not in g:
                    g.add_node(ext_id, label=target, file="(external)", kind="external", title=target)
                g.add_edge(f.node_id, ext_id, kind=dtype)
            # builtin / unresolved: omitted from the graph to keep it readable
    return g


def render_interactive_html(g: nx.DiGraph, outpath: Path):
    from pyvis.network import Network

    net = Network(height="800px", width="100%", directed=True, notebook=False,
                   bgcolor="#ffffff", font_color="#222222")
    net.barnes_hut(gravity=-6000, spring_length=120)

    file_colors: dict[str, str] = {}
    palette = ["#7F77DD", "#1D9E75", "#D85A30", "#D4537E", "#378ADD", "#639922", "#BA7517"]

    for node, attrs in g.nodes(data=True):
        if attrs.get("kind") == "external":
            color = "#B4B2A9"
            shape = "box"
        else:
            f = attrs.get("file", "?")
            if f not in file_colors:
                file_colors[f] = palette[len(file_colors) % len(palette)]
            color = file_colors[f]
            shape = "dot"
        net.add_node(node, label=attrs.get("label", node), title=attrs.get("title", node),
                     color=color, shape=shape)

    for u, v, attrs in g.edges(data=True):
        dashed = attrs.get("kind") != "internal"
        net.add_edge(u, v, arrows="to", dashes=dashed)

    net.set_options("""
    { "physics": { "stabilization": { "iterations": 150 } } }
    """)
    net.write_html(str(outpath), notebook=False)


def render_static_png(g: nx.DiGraph, outpath: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(g, k=0.6, seed=42)

    internal_nodes = [n for n, a in g.nodes(data=True) if a.get("kind") != "external"]
    external_nodes = [n for n, a in g.nodes(data=True) if a.get("kind") == "external"]

    nx.draw_networkx_nodes(g, pos, nodelist=internal_nodes, node_color="#7F77DD", node_size=500)
    nx.draw_networkx_nodes(g, pos, nodelist=external_nodes, node_color="#B4B2A9", node_size=350, node_shape="s")
    nx.draw_networkx_edges(g, pos, arrows=True, arrowsize=10, alpha=0.5)
    labels = {n: g.nodes[n].get("label", n) for n in g.nodes}
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=7)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outpath, dpi=180)
    plt.close()


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

# def main():
#     parser = argparse.ArgumentParser(description="Scan a Python project and report function metadata + dependencies.")
#     parser.add_argument("directory", help="Path to the Python project/directory to scan")
#     parser.add_argument("--outdir", default="./scan_output", help="Where to write reports (default: ./scan_output)")
#     parser.add_argument("--exclude", default="", help="Comma-separated extra folder names to skip")
#     args = parser.parse_args()

#     root = Path(args.directory).resolve()
#     if not root.is_dir():
#         print(f"Not a directory: {root}", file=sys.stderr)
#         sys.exit(1)

#     excludes = set(DEFAULT_EXCLUDES) | {e.strip() for e in args.exclude.split(",") if e.strip()}
#     outdir = Path(args.outdir)
#     outdir.mkdir(parents=True, exist_ok=True)

#     print(f"Scanning {root} ...")
#     scanner = ProjectScanner(root, excludes)
#     scanner.scan()
#     print(f"Found {len(scanner.functions)} functions across "
#           f"{len({f.file_name for f in scanner.functions})} files.")

#     export_json(scanner.functions, outdir / "functions_report.json")
#     export_markdown(scanner.functions, outdir / "functions_report.md")

#     g = build_graph(scanner.functions)
#     render_interactive_html(g, outdir / "dependency_graph.html")
#     render_static_png(g, outdir / "dependency_graph.png")

#     print(f"Wrote reports to {outdir}/")

# Global variables
DEFAULT_PROJECT_DIRECTORY = r"E:\WORK\PROJECT\git\PersonalAssistant"
DEFAULT_OUTPUT_DIRECTORY = r"E:\WORK\PROJECT\git\PersonalAssistant\UI\InfoExtractor\Output"


def main():
    parser = argparse.ArgumentParser(
        description="Scan a Python project and report function metadata + dependencies."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=DEFAULT_PROJECT_DIRECTORY,
        help=f"Path to the Python project/directory to scan (default: {DEFAULT_PROJECT_DIRECTORY})",
    )

    parser.add_argument(
        "--outdir",
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=f"Where to write reports (default: {DEFAULT_OUTPUT_DIRECTORY})",
    )

    parser.add_argument(
        "--exclude",
        default="",
        help="Comma-separated extra folder names to skip",
    )

    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    outdir = Path(args.outdir).resolve()

    if not directory.is_dir():
        print(f"Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    excludes = set(DEFAULT_EXCLUDES) | {
        e.strip() for e in args.exclude.split(",") if e.strip()
    }

    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning {directory} ...")

    scanner = ProjectScanner(directory, excludes)
    scanner.scan()

    print(
        f"Found {len(scanner.functions)} functions across "
        f"{len({f.file_name for f in scanner.functions})} files."
    )

    export_json(scanner.functions, outdir / "functions_report.json")
    export_markdown(scanner.functions, outdir / "functions_report.md")

    g = build_graph(scanner.functions)
    render_interactive_html(g, outdir / "dependency_graph.html")
    render_static_png(g, outdir / "dependency_graph.png")

    print(f"Wrote reports to {outdir}/")

if __name__ == "__main__":
    main()