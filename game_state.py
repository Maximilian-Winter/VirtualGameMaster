import os
import yaml
import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any


class GameState:
    def __init__(self, initial_state_file: str):
        self.template_fields = self.load_yaml_initial_game_state(initial_state_file)

    def load_yaml_initial_game_state(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}

        try:
            with open(file_path, 'r') as file:
                yaml_content = yaml.safe_load(file)
                return self._process_yaml_content(yaml_content)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}

    def _process_yaml_content(self, content: Dict[str, Any]) -> Dict[str, str]:
        return {k: self._process_value(v) for k, v in content.items()}

    def _process_value(self, v, indent=0):
        if isinstance(v, list):
            if any(isinstance(item, dict) and 'name' in item for item in v):
                return '\n'.join(self._process_special_item(item, indent) for item in v)
            return '\n'.join(self._process_list_item(item, indent) for item in v)
        elif isinstance(v, dict):
            return self._process_dict(v, indent)
        elif isinstance(v, str):
            return v.strip()
        else:
            return str(v)

    def _process_list_item(self, item, indent=0):
        if isinstance(item, dict):
            result = []
            for key, value in item.items():
                if isinstance(value, list):
                    result.append(f"{' ' * indent}- {key}:")
                    for subitem in value:
                        result.append(f"{' ' * (indent + 2)}- {subitem}")
                else:
                    result.append(f"{' ' * indent}- {key}: {self._process_value(value, indent + 2)}")
            return '\n'.join(result)
        else:
            return f"{' ' * indent}- {item}"

    def _process_dict(self, d, indent=0):
        result = []
        for key, value in d.items():
            if isinstance(value, dict):
                result.append(f"{' ' * indent}{key}:")
                result.append(self._process_dict(value, indent + 2))
            elif isinstance(value, list):
                result.append(f"{' ' * indent}{key}:")
                result.append(self._process_value(value, indent + 2))
            else:
                result.append(f"{' ' * indent}{key}: {self._process_value(value, indent + 2)}")
        return '\n'.join(result)

    def _process_special_item(self, item, indent=0):
        result = []
        for key, value in item.items():
            if isinstance(value, list):
                result.append(f"{' ' * indent}{key}:")
                for subitem in value:
                    result.append(f"{' ' * (indent + 2)}- {subitem}")
            else:
                result.append(f"{' ' * indent}{key}: {value}")
        return '\n'.join(result)

    def update_from_xml(self, xml_string: str) -> None:
        xml_string = f"<root>{xml_string}</root>"
        try:
            root = ET.fromstring(xml_string)
            self._process_element(root)
        except ET.ParseError:
            self._update_from_regex(xml_string)

    def _process_element(self, element: ET.Element) -> None:
        for child in element:
            if len(child) == 0:  # If the element has no children
                key = child.tag.split('.')[-1]
                self.template_fields[key] = child.text.strip() if child.text else ""
            else:
                self._process_element(child)

    def _update_from_regex(self, content: str) -> None:
        sections = re.findall(r'<([\w.]+)>(.*?)</\1>', content, re.DOTALL)
        for section, content in sections:
            key = section.split('.')[-1]
            self.template_fields[key] = content.strip()

    def save_json(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.template_fields, f, indent=2)

    def load_json(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.template_fields = json.load(f)

    def get_field(self, key: str, default: Any = None) -> Any:
        return self.template_fields.get(key, default)

    def set_field(self, key: str, value: Any) -> None:
        self.template_fields[key] = value

    def __str__(self) -> str:
        return f"GameState(fields: {len(self.template_fields)})"
