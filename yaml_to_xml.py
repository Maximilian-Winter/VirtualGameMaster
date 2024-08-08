import yaml
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def yaml_to_xml(yaml_file):
    # Load YAML data
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Helper function to convert YAML to XML recursively
    def dict_to_xml(tag, d):
        elem = Element(tag)
        for key, val in d.items():
            child = SubElement(elem, key)
            if isinstance(val, dict):
                child = dict_to_xml(key, val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        dict_to_xml(key, item)
                    else:
                        SubElement(child, 'item').text = str(item)
            else:
                child.text = str(val).strip()
        return elem

    # Convert YAML to XML
    root = dict_to_xml('game_state', yaml_data)

    # Convert XML to string and pretty print
    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    return pretty_xml


# Example usage
xml_output = yaml_to_xml('game_starters/rpg_candlekeep.yaml')
print(xml_output)

# Optionally, save to file
with open('output.xml', 'w') as file:
    file.write(xml_output)
