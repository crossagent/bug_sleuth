
import os
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser, Node
import logging

class CodeParser:
    def __init__(self):
        self.language = Language(tscsharp.language())
        self.parser = Parser(self.language)
        self.logger = logging.getLogger("CodeIndexer.Parser")

    def parse_file(self, file_path: str):
        """Parses a C# file and yields definition symbols."""
        try:
            with open(file_path, 'rb') as f: # Tree-sitter expects bytes
                blob = f.read()
            
            tree = self.parser.parse(blob)
            root = tree.root_node
            
            # Start recursion
            yield from self._visit_node(root, blob)
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")

    def _visit_node(self, node: Node, source_bytes: bytes):
        """Recursively visits nodes to find definitions."""
        
        # Check if node is a definition we care about
        symbol_type = self._get_symbol_type(node.type)
        
        if symbol_type:
            name = self._extract_name(node, source_bytes)
            if name:
                yield {
                    "name": name,
                    "type": symbol_type,
                    "start_line": node.start_point.row, # 0-indexed
                    "end_line": node.end_point.row # 0-indexed
                }
        
        # Recurse
        for child in node.children:
            yield from self._visit_node(child, source_bytes)

    def _get_symbol_type(self, node_type: str):
        """Maps tree-sitter node types to our symbol types."""
        MAPPING = {
            "class_declaration": "class",
            "struct_declaration": "struct",
            "interface_declaration": "interface",
            "enum_declaration": "enum",
            "method_declaration": "method",
            "constructor_declaration": "constructor",
            #"field_declaration": "field", # Fields can be noisy, enabling if needed. user wanted definitions? usually methods are key. Let's include fields for strictness but maybe filter later.
            "property_declaration": "property"
        }
        return MAPPING.get(node_type)

    def _extract_name(self, node: Node, source_bytes: bytes) -> str:
        """Extracts the identifier name from a declaration node."""
        # For most declarations, there is a child field named 'name' or just an identifier node
        name_node = node.child_by_field_name("name")
        
        if not name_node:
            # Fallback: iterate children to find 'identifier'
            for child in node.children:
                if child.type == "identifier":
                    name_node = child
                    break
        
        if name_node:
            return source_bytes[name_node.start_byte : name_node.end_byte].decode('utf-8')
        
        return None
