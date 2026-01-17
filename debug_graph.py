import re

class SymbolGraphBuilder:
    def __init__(self, lang_name="python"):
        # We simulate the interface so main.py doesn't need to change
        self.lang = lang_name

    def parse_symbols(self, code):
        """Extract symbols using high-speed regex"""
        symbols = []
        
        # Matches 'def name' or 'class Name'
        # Handles indentation (methods) and async def
        pattern = re.compile(r'^\s*(async\s+)?(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
        
        for m in pattern.finditer(code):
            is_async = m.group(1) is not None
            keyword = m.group(2)
            name = m.group(3)
            
            symbols.append({
                "name": name,
                "type": "function" if keyword == "def" else "class",
                "line": code.count('\n', 0, m.start()) + 1
            })
            
        return symbols

