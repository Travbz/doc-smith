from datetime import datetime
import re
import json
from typing import Dict, List, Any, Optional

class DocGenerator:
    """Tool for generating documentation from code analysis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.templates = self._load_templates()
    
    def generate_documentation(self, analysis: Dict[str, Any]) -> str:
        """Generate documentation from code analysis."""
        doc_type = self._determine_doc_type(analysis)
        template = self.templates.get(doc_type, self.templates['default'])
        
        metadata = self._generate_metadata(analysis)
        content = template.format(
            metadata=metadata,
            overview=self._generate_overview(analysis),
            installation=self._generate_installation(analysis),
            usage=self._generate_usage(analysis),
            api=self._generate_api_reference(analysis),
            examples=self._generate_examples(analysis)
        )
        
        return self._post_process(content)
    
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates."""
        return {
            'default': '''# {metadata}

{overview}

{installation}

{usage}

{api}

{examples}
''',
            'component': '''# {metadata}

{overview}

## Props

{api}

## Usage

{usage}

## Examples

{examples}
''',
            'library': '''# {metadata}

{overview}

## Installation

{installation}

## Usage

{usage}

## API Reference

{api}

## Examples

{examples}
'''
        }
    
    def _determine_doc_type(self, analysis: Dict[str, Any]) -> str:
        """Determine the type of documentation needed."""
        if 'React' in analysis.get('frameworks', []):
            return 'component'
        if len(analysis.get('components', [])) > 5:
            return 'library'
        return 'default'

    def _generate_metadata(self, analysis: Dict[str, Any]) -> str:
        """Generate documentation metadata."""
        filename = analysis['file'].split('/')[-1]
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        return f"{filename}\n{'=' * len(filename)}\n\n" + \
               f"- **Language**: {analysis['language']}\n" + \
               f"- **Updated**: {timestamp}\n" + \
               "- **Type**: " + self._determine_doc_type(analysis).title() + "\n\n"

    def _generate_code_example(self, analysis: Dict[str, Any], component: Dict[str, Any]) -> str:
        """Generate example code based on component type and language."""
        if 'React' in analysis.get('frameworks', []):
            props = component.get('props', [])
            prop_string = ' '.join(f'{prop["name"]}={{{prop.get("default", "value")}}}' 
                                 for prop in props if prop.get('required', False))
            return f"""
import {{ {component['name']} }} from './components/{component['name']}';

function Example() {{
    return (
        <{component['name']} {prop_string} />
    );
}}
"""
        elif component['type'] == 'class':
            return f"""
// Create an instance
const instance = new {component['name']}();

// Example usage
instance.someMethod();
"""
        else:
            return f"""
// Example usage of {component['name']}
{component['name']}();
"""

    def _post_process(self, content: str) -> str:
        """Post-process the generated documentation."""
        # Remove multiple blank lines
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Ensure consistent heading spacing
        content = re.sub(r'\n#+\s*', '\n\n# ', content)
        
        # Add table of contents if needed
        if self.config.get('include_toc', True):
            toc = self._generate_toc(content)
            content = f"{toc}\n\n{content}"
        
        return content.strip() + '\n'

    def _generate_toc(self, content: str) -> str:
        """Generate table of contents from headings."""
        toc = "## Table of Contents\n\n"
        
        # Find all headings
        headings = re.findall(r'^(#{1,6})\s*(.+)$', content, re.MULTILINE)
        
        for level, title in headings:
            # Skip the title itself and the TOC
            if title.lower() == 'table of contents' or len(level) == 1:
                continue
                
            indent = '  ' * (len(level) - 2)
            link = title.lower().replace(' ', '-')
            toc += f"{indent}- [{title}](#{link})\n"
        
        return toc

    def _generate_api_examples(self, component: Dict[str, Any]) -> str:
        """Generate API usage examples for a component."""
        examples = {}
        
        if component['type'] == 'class':
            examples['instantiation'] = f"""
const instance = new {component['name']}();
"""
            if 'methods' in component:
                for method in component['methods']:
                    examples[f"method_{method['name']}"] = f"""
// Using {method['name']} method
instance.{method['name']}({', '.join(method.get('parameters', []))});
"""
                    
        elif component['type'] == 'function':
            params = component.get('parameters', [])
            param_list = ', '.join(p.get('name', f'param{i}') for i, p in enumerate(params))
            examples['basic_usage'] = f"""
const result = {component['name']}({param_list});
"""

        return examples

    def _format_type_definition(self, type_info: Dict[str, Any]) -> str:
        """Format type definition in the appropriate language style."""
        if isinstance(type_info, str):
            return type_info
            
        type_name = type_info.get('name', 'any')
        
        if type_info.get('isArray', False):
            return f"{type_name}[]"
            
        if type_info.get('isOptional', False):
            return f"{type_name} | undefined"
            
        return type_name

    def _generate_error_handling(self, analysis: Dict[str, Any]) -> str:
        """Generate error handling documentation."""
        patterns = analysis['analysis'].get('patterns', [])
        error_patterns = [p for p in patterns if 'error' in p['name'].lower()]
        
        if not error_patterns:
            return ""
            
        content = "## Error Handling\n\n"
        for pattern in error_patterns:
            content += f"### {pattern['name']}\n\n"
            content += f"{pattern.get('description', '')}\n\n"
            if 'example' in pattern:
                content += "```" + analysis['language'].lower() + "\n"
                content += pattern['example'] + "\n"
                content += "```\n\n"
                
        return content

    def _add_typescript_types(self, analysis: Dict[str, Any]) -> str:
        """Add TypeScript type definitions if applicable."""
        if analysis['language'] not in ['TypeScript', 'React/TypeScript']:
            return ""
            
        types = []
        for component in analysis['analysis'].get('components', []):
            if component['type'] == 'interface':
                types.append(self._format_interface(component))
            elif component['type'] == 'type':
                types.append(self._format_type_alias(component))
                
        if not types:
            return ""
            
        return "\n## Type Definitions\n\n" + "\n\n".join(types)

    def _format_interface(self, interface: Dict[str, Any]) -> str:
        """Format TypeScript interface documentation."""
        content = f"### `{interface['name']}`\n\n"
        content += f"{interface.get('description', '')}\n\n"
        
        if 'properties' in interface:
            content += "| Property | Type | Description |\n"
            content += "|----------|------|-------------|\n"
            for prop in interface['properties']:
                content += f"| {prop['name']} | "
                content += f"{self._format_type_definition(prop['type'])} | "
                content += f"{prop.get('description', '')} |\n"
                
        return content

    def _format_type_alias(self, type_def: Dict[str, Any]) -> str:
        """Format TypeScript type alias documentation."""
        content = f"### `{type_def['name']}`\n\n"
        content += f"{type_def.get('description', '')}\n\n"
        
        if 'definition' in type_def:
            content += "```typescript\n"
            content += f"type {type_def['name']} = {type_def['definition']};\n"
            content += "```\n"
            
        return content