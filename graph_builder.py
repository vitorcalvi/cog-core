import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


class SymbolGraphBuilder:
    def __init__(self, lang_name="python"):
        self.language = get_language(lang_name)
        self.parser = get_parser(lang_name)
        # Map of resource name to operations that use it
        self.resource_dependencies = defaultdict(set)
        # Map of operation to resources it depends on
        self.operation_resources = defaultdict(set)

    def parse_symbols(self, code):
        tree = self.parser.parse(bytes(code, "utf8"))

        query = self.language.query("""
            (function_definition name: (identifier) @name)
            (class_definition name: (identifier) @name)
        """)

        symbols = []

        # STRATEGY: Try passing query to constructor (0.23 style)
        # If that fails (TypeError), try empty constructor (0.21/0.25 style)
        try:
            # Try 0.23 style: Cursor is bound to a specific query
            cursor = tree_sitter.QueryCursor(query)

            # In this version, captures/matches usually take just the node
            # matches() -> iterator of matches
            # captures() -> iterator of (Node, str)
            if hasattr(cursor, "captures"):
                results = cursor.captures(tree.root_node)
            else:
                # Some versions use execute() or similar, but let's try matches fallback
                results = []  # Fallback

        except TypeError:
            # Fallback to 0.21/0.25 style: Cursor is reusable
            cursor = tree_sitter.QueryCursor()
            # Then we pass query to the method
            results = cursor.captures(query, tree.root_node)

        # Process whatever results we got (assuming they are iterable of (Node, index/name))
        # Note: 'results' might be different formats, so we inspect robustly

        if not results and hasattr(query, "captures"):
            # Last resort: 0.21 legacy style on Query object
            results = query.captures(tree.root_node)

        # Iterate safely
        for item in results:
            # Item structure varies: (Node, str) or (Node, int) or Match object
            node = None
            tag = "unknown"

            if isinstance(item, tuple) and len(item) == 2:
                node, tag = item
            elif hasattr(item, "node"):
                node = item.node  # If it's a dedicated Capture object

            if node:
                symbols.append(
                    {
                        "name": node.text.decode("utf8"),
                        "type": "function"
                        if "function" in node.parent.type
                        else "class",
                        "line": node.start_point[0] + 1,
                    }
                )

        return symbols

    def extract_resource_dependencies(self, symbols, code):
        """
        Extract resource dependencies from operations.

        Args:
            symbols: List of extracted symbols from parse_symbols
            code: The source code to analyze

        Returns:
            Tuple of (resource_deps, op_resources)
        """
        # Clear previous mappings
        self.resource_dependencies.clear()
        self.operation_resources.clear()

        # In Python, look for function parameters and their usage
        for symbol in symbols:
            if symbol["type"] == "function":
                func_name = symbol["name"]
                lines = code.split("\n")

                # Get function body (simplified approach)
                start_line = symbol["line"] - 1
                end_line = len(lines)

                # Look for next function or class definition to determine end
                for i in range(start_line + 1, end_line):
                    line = lines[i].strip()
                    if line.startswith(("def ", "class ", "async def ")):
                        end_line = i
                        break

                func_body = "\n".join(lines[start_line:end_line])

                # Extract potential resources from function signature and body
                resources = self._extract_resources_from_function(func_body)

                # Map the operation to its resources
                self.operation_resources[func_name] = resources

                # Map each resource to the operation
                for resource in resources:
                    self.resource_dependencies[resource].add(func_name)

        return dict(self.resource_dependencies), dict(self.operation_resources)

    def _extract_resources_from_function(self, func_code):
        """
        Extract resource names from a function code.

        Args:
            func_code: The function's source code

        Returns:
            Set of resource names
        """
        resources = set()
        lines = func_code.split("\n")

        # Look for function definition line
        for line in lines:
            if line.strip().startswith(("def ", "async def ")):
                # Extract parameters from function signature
                params = self._extract_function_params(line)
                resources.update(params)

        # Look for common resource usage patterns
        resource_patterns = [
            # File operations
            (r'\.open\s*\(\s*[\'"]([^\'"]+)[\'"]', "file"),
            # Database connections
            (r"(connect|connection|cursor|execute|query)", "database"),
            # HTTP requests
            (r"(get|post|put|delete|request)\s*\(", "http"),
            # Variables with可疑 names
            (r"\b(config|settings|resource|data_|input_|output_)\w*", "config"),
        ]

        for line in lines:
            # Skip comments
            if line.strip().startswith("#"):
                continue

            for pattern, resource_type in resource_patterns:
                import re

                matches = re.findall(pattern, line.lower())
                if matches:
                    if resource_type in ("file", "config"):
                        # Extract actual names
                        resources.update(matches)
                    else:
                        # Use type as resource identifier
                        resources.add(f"{resource_type}_{len(resources)}")

        return resources

    def _extract_function_params(self, func_def_line):
        """
        Extract parameter names from a function definition line.

        Args:
            func_def_line: A line containing `def function_name(params):`

        Returns:
            Set of parameter names
        """
        params = set()

        # Find parameters between parentheses
        import re

        match = re.search(r"\((.*?)\)", func_def_line)
        if match:
            param_str = match.group(1)
            # Split and clean parameter names
            for param in param_str.split(","):
                param = param.strip()
                # Handle default values and type hints
                param = param.split(":")[0].split("=")[0].strip()
                if param and param != "self":
                    params.add(param)

        return params

    def build_dependency_graph(self):
        """
        Build a NetworkX graph representing resource dependencies.

        Returns:
            NetworkX DiGraph object
        """
        G = nx.DiGraph()

        # Add nodes for operations
        for op_name in self.operation_resources:
            G.add_node(op_name, type="operation")

        # Add nodes for resources and edges for dependencies
        for resource, operations in self.resource_dependencies.items():
            # Add resource node
            G.add_node(resource, type="resource")
            # Add edges from operations to resources
            for op in operations:
                G.add_edge(op, resource, relation="uses")

        return G

    def visualize_graph(self, output_file=None):
        """
        Visualize the dependency graph using matplotlib.

        Args:
            output_file: Optional file path to save the visualization
        """
        G = self.build_dependency_graph()

        plt.figure(figsize=(12, 8))

        # Set node colors based on type
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get("type") == "operation":
                node_colors.append("lightblue")
            else:
                node_colors.append("lightgreen")

        # Draw the graph
        pos = nx.spring_layout(G, seed=42)
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=2000,
            font_size=10,
            font_weight="bold",
            arrowsize=20,
            edge_color="gray",
        )

        # Add legend
        plt.scatter([], [], c="lightblue", s=200, label="Operation")
        plt.scatter([], [], c="lightgreen", s=200, label="Resource")
        plt.legend()

        plt.title("Resource Dependency Graph")

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.show()


def analyze_dependencies(self):
    """
    Analyze and return dependency insights.

    Returns:
        Dictionary with dependency statistics and insights
    """
    insights = {
        "total_operations": len(self.operation_resources),
        "total_resources": len(self.resource_dependencies),
        "resource_usage": {},
        "operation_dependencies": {},
        "shared_resources": {},
        "critical_resources": [],
    }

    # Resource usage frequency
    for resource, operations in self.resource_dependencies.items():
        insights["resource_usage"][resource] = len(operations)

        # Find shared resources (used by multiple operations)
        if len(operations) > 1:
            insights["shared_resources"][resource] = list(operations)

    # Operation dependencies (how many resources each operation needs)
    for operation, resources in self.operation_resources.items():
        insights["operation_dependencies"][operation] = len(resources)

    # Critical resources (used by most operations)
    if insights["total_resources"] > 0 and insights["resource_usage"]:
        avg_usage = sum(insights["resource_usage"].values()) / len(
            insights["resource_usage"]
        )
        insights["critical_resources"] = [
            r
            for r, count in insights["resource_usage"].items()
            if isinstance(count, int) and count > avg_usage * 1.5
        ]

    return insights
