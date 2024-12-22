import os
import ast
import json
import re
from typing import Dict, List, Any, Optional

class CodeAnalyzer:
    """Tool for analyzing source code files."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a source code file."""
        with open(file_path, 'r') as f:
            code = f.read()
        
        language = self._detect_language(file_path)
        analyzer = self._get_analyzer(language)
        
        analysis = analyzer(code) if analyzer else self._generic_analysis(code)
        
        return {
            "file": file_path,
            "language": language,
            "code": code,
            "analysis": analysis
        }

    def _analyze_typescript(self, code: str) -> Dict[str, Any]:
        """Analyze TypeScript source code."""
        # Extract interfaces
        interface_pattern = r'interface\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
        interfaces = [{'name': m.group(1), 'extends': m.group(2)} 
                     for m in re.finditer(interface_pattern, code)]
        
        # Extract types
        type_pattern = r'type\s+(\w+)\s*=\s*'
        types = [m.group(1) for m in re.finditer(type_pattern, code)]
        
        # Get JS analysis as base
        js_analysis = self._analyze_javascript(code)
        
        # Add TypeScript-specific components
        js_analysis['components'].extend([
            {
                "name": interface['name'],
                "type": "interface",
                "description": f"Interface{' extending ' + interface['extends'] if interface['extends'] else ''}"
            }
            for interface in interfaces
        ])
        
        js_analysis['components'].extend([
            {
                "name": type_name,
                "type": "type",
                "description": "Type definition"
            }
            for type_name in types
        ])
        
        return js_analysis

    def _analyze_react(self, code: str) -> Dict[str, Any]:
        """Analyze React component code."""
        # Get base analysis from JS/TS
        base_analysis = (self._analyze_typescript(code) 
                        if code.endswith('.tsx') 
                        else self._analyze_javascript(code))
        
        # Extract React components
        component_pattern = r'(?:class\s+(\w+)\s+extends\s+React\.Component)|(?:function\s+(\w+)\s*\([^)]*\)\s*{[^}]*(?:return|=>)\s*\(?[\s\n]*<)'
        components = [m.group(1) or m.group(2) for m in re.finditer(component_pattern, code)]
        
        # Extract hooks usage
        hook_pattern = r'use[A-Z]\w+'
        hooks = list(set(re.findall(hook_pattern, code)))
        
        # Extract JSX patterns
        jsx_pattern = r'<([A-Z]\w+)[^>]*>'
        jsx_components = list(set(re.findall(jsx_pattern, code)))
        
        # Add React-specific information
        base_analysis['frameworks'] = ['React']
        base_analysis['components'].extend([
            {
                "name": comp_name,
                "type": "react_component",
                "description": "React component"
            }
            for comp_name in components
        ])
        
        base_analysis['patterns'].extend([
            {
                "name": "React Hooks",
                "items": hooks,
                "description": "React hooks used in the component"
            },
            {
                "name": "JSX Components",
                "items": jsx_components,
                "description": "JSX components used in the template"
            }
        ])
        
        return base_analysis

    def _detect_patterns(self, code: str) -> List[Dict[str, str]]:
        """Detect common code patterns."""
        patterns = []
        
        # Design patterns
        pattern_indicators = {
            "Singleton": r'private\s+static\s+instance|static\s+getInstance',
            "Factory": r'create\w+|factory',
            "Observer": r'subscribe|observer|addEventListener',
            "Strategy": r'strategy|algorithm',
            "Decorator": r'decorator|@\w+',
        }
        
        for pattern, regex in pattern_indicators.items():
            if re.search(regex, code, re.IGNORECASE):
                patterns.append({
                    "name": pattern,
                    "type": "design_pattern",
                    "description": f"Possible {pattern} pattern detected"
                })
        
        # Error handling
        if re.search(r'try\s*{|catch\s*\(|throw\s+|Promise\.catch', code):
            patterns.append({
                "name": "Error Handling",
                "type": "practice",
                "description": "Implements error handling"
            })
        
        # Async patterns
        if re.search(r'async|await|Promise|\.then', code):
            patterns.append({
                "name": "Asynchronous Processing",
                "type": "practice",
                "description": "Uses async/await or Promises"
            })
        
        return patterns

    def _generic_analysis(self, code: str) -> Dict[str, Any]:
        """Perform generic code analysis when language-specific analysis isn't available."""
        # Extract possible functions
        function_pattern = r'(?:function|def|fun|fn)\s+(\w+)\s*\('
        functions = list(set(re.findall(function_pattern, code)))
        
        # Extract possible classes
        class_pattern = r'(?:class)\s+(\w+)'
        classes = list(set(re.findall(class_pattern, code)))
        
        # Extract possible imports
        import_pattern = r'(?:import|require|use|include)\s+[\'"]*([^\s\'"]+)'
        imports = list(set(re.findall(import_pattern, code)))
        
        return {
            "overview": {
                "purpose": self._extract_file_description(code),
                "key_features": functions + classes
            },
            "components": [
                *[{
                    "name": f,
                    "type": "function",
                    "description": "Function definition"
                } for f in functions],
                *[{
                    "name": c,
                    "type": "class",
                    "description": "Class definition"
                } for c in classes]
            ],
            "patterns": self._detect_patterns(code),
            "dependencies": [{"name": imp, "type": "import"} for imp in imports]
        }

    def _extract_file_description(self, code: str) -> str:
        """Extract file description from code comments."""
        # Try to find a block comment at the start of the file
        block_comment_pattern = r'/\*\*(.*?)\*/'
        match = re.search(block_comment_pattern, code[:500], re.DOTALL)
        if match:
            return self._clean_comment(match.group(1))
        
        # Try to find consecutive single-line comments
        single_comments_pattern = r'(?:^|\n)(?:\s*//[^\n]*\n)+'
        match = re.search(single_comments_pattern, code[:500])
        if match:
            return self._clean_comment(match.group(0))
        
        return "No file description available"

    def _clean_comment(self, comment: str) -> str:
        """Clean up extracted comments."""
        # Remove comment markers and excessive whitespace
        lines = comment.replace('*', '').replace('/', '').split('\n')
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
        return ' '.join(lines)