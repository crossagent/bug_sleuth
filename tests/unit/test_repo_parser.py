import pytest
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp

def test_csharp_parser_initialization():
    """Verify that the C# parser can be initialized and parse basic code."""
    CS_LANGUAGE = Language(tscsharp.language())
    parser = Parser(CS_LANGUAGE)
    
    code = b"""
    using System;
    namespace Test {
        public class Demo { }
    }
    """
    
    tree = parser.parse(code)
    root = tree.root_node
    
    assert root.type == "compilation_unit"
    assert root.child_count > 0

def test_csharp_parser_traversal():
    """Verify we can traverse the tree."""
    CS_LANGUAGE = Language(tscsharp.language())
    parser = Parser(CS_LANGUAGE)
    
    code = b"public class Foo { }"
    tree = parser.parse(code)
    
    # Find class declaration
    found_class = False
    cursor = tree.walk()
    
    # BFS/DFS check
    to_visit = [cursor.node]
    while to_visit:
        node = to_visit.pop(0)
        if node.type == "class_declaration":
            found_class = True
            break
        to_visit.extend(node.children)
            
    assert found_class, "Should find a class_declaration node"
