import os
from typing import Dict, Any

import yaml


def load_yaml_initial_game_state(file_path: str) -> Dict[str, Any]:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                yaml_content = yaml.safe_load(file)

                def process_value(v):
                    if isinstance(v, list):
                        return '\n'.join(process_list_item(item) for item in v)
                    elif isinstance(v, dict):
                        return process_dict(v)
                    elif isinstance(v, str):
                        return v.strip()
                    else:
                        return str(v)

                def process_list_item(item):
                    if isinstance(item, dict):
                        return '\n'.join(f"- {key}: {value}" for key, value in item.items())
                    else:
                        return f"- {item}"

                def process_dict(d):
                    result = []
                    for key, value in d.items():
                        if isinstance(value, dict):
                            result.append(f"{key}:")
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, list):
                                    result.append(f"  {sub_key}:")
                                    result.extend(f"    - {item}" for item in sub_value)
                                else:
                                    result.append(f"  {sub_key}: {sub_value}")
                        else:
                            result.append(f"{key}: {process_value(value)}")
                    return '\n'.join(result)

                return {k: process_value(v) for k, v in yaml_content.items()}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}
    else:
        return {}