import os
from typing import Dict, Any

import yaml

def load_yaml_initial_game_state(file_path: str) -> Dict[str, Any]:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                yaml_content = yaml.safe_load(file)

                def process_value(v, indent=0):
                    if isinstance(v, list):
                        if any(isinstance(item, dict) and 'name' in item for item in v):
                            # This is likely the special_items list
                            return '\n'.join(process_special_item(item, indent) for item in v)
                        return '\n'.join(process_list_item(item, indent) for item in v)
                    elif isinstance(v, dict):
                        return process_dict(v, indent)
                    elif isinstance(v, str):
                        return v.strip()
                    else:
                        return str(v)

                def process_list_item(item, indent=0):
                    if isinstance(item, dict):
                        result = []
                        for key, value in item.items():
                            if isinstance(value, list):
                                result.append(f"{' ' * indent}- {key}:")
                                for subitem in value:
                                    result.append(f"{' ' * (indent+2)}- {subitem}")
                            else:
                                result.append(f"{' ' * indent}- {key}: {process_value(value, indent+2)}")
                        return '\n'.join(result)
                    else:
                        return f"{' ' * indent}- {item}"

                def process_dict(d, indent=0):
                    result = []
                    for key, value in d.items():
                        if isinstance(value, dict):
                            result.append(f"{' ' * indent}{key}:")
                            result.append(process_dict(value, indent+2))
                        elif isinstance(value, list):
                            result.append(f"{' ' * indent}{key}:")
                            result.append(process_value(value, indent+2))
                        else:
                            result.append(f"{' ' * indent}{key}: {process_value(value, indent+2)}")
                    return '\n'.join(result)

                def process_special_item(item, indent=0):
                    result = []
                    for key, value in item.items():
                        if isinstance(value, list):
                            result.append(f"{' ' * indent}{key}:")
                            for subitem in value:
                                result.append(f"{' ' * (indent+2)}- {subitem}")
                        else:
                            result.append(f"{' ' * indent}{key}: {value}")
                    return '\n'.join(result)

                return {k: process_value(v) for k, v in yaml_content.items()}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}
    else:
        return {}