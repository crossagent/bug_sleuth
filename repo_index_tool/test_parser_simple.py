
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser

def test_parsing():
    print(">>> Initializing C# Parser...")
    CS_LANGUAGE = Language(tscsharp.language())
    parser = Parser(CS_LANGUAGE)
    
    code = b"""
    using System;
    namespace Game {
        public class BattleManager : MonoBehaviour {
            public int health = 100;
            public void Explode() {
                Console.WriteLine("Boom!");
            }
        }
    }
    """
    
    print(">>> Parsing Code Snippet...")
    tree = parser.parse(code)
    root_node = tree.root_node
    
    print(f">>> Root Node Type: {root_node.type}")
    print(f">>> Child Count: {root_node.child_count}")
    
    # Simple traversal
    cursor = tree.walk()
    visited_children = False
    while True:
        if not visited_children:
            print(f"Node: {cursor.node.type} [{cursor.node.start_point} - {cursor.node.end_point}]")
            
        if cursor.goto_first_child():
            visited_children = False
        elif cursor.goto_next_sibling():
            visited_children = False
        elif cursor.goto_parent():
            visited_children = True
        else:
            break
            
    print(">>> Test Finished Successfully.")

if __name__ == "__main__":
    test_parsing()
