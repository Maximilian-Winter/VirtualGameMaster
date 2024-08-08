import yaml
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
import xml.etree.ElementTree as ET


def clean_tag(tag):
    return tag.replace(" ", "-").replace("_", "-").replace("'", "")


def yaml_to_xml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        yaml_data = yaml.safe_load(file)

    def dict_to_xml(tag, d):
        elem = Element(clean_tag(tag))
        for key, val in d.items():
            key = clean_tag(str(key))
            if isinstance(val, dict):
                child = SubElement(elem, key)
                for sub_key, sub_val in val.items():
                    dict_to_xml(sub_key, {sub_key: sub_val}).find(clean_tag(str(sub_key)))
                    child.append(dict_to_xml(sub_key, {sub_key: sub_val}).find(clean_tag(str(sub_key))))
            elif isinstance(val, list):
                child = SubElement(elem, key)
                for item in val:
                    if isinstance(item, dict):
                        child.append(dict_to_xml('item', item))
                    else:
                        list_item = SubElement(child, 'item')
                        list_item.text = str(item).strip()
            else:
                child = SubElement(elem, key)
                child.text = str(val).strip()
        return elem

    root = dict_to_xml('game-state', yaml_data)
    return root


def merge_xml_update(original_root, update_string):
    update_root = ET.fromstring(update_string)

    def recursive_update(original_element, update_element):
        for update_child in update_element:
            matching_original = original_element.find(update_child.tag)
            if matching_original is None or matching_original.tag == "item":
                # If the element doesn't exist in the original, append it
                original_element.append(update_child)
            else:
                if len(update_child) == 0:
                    # If it's a leaf node, update the text
                    matching_original.text = update_child.text
                else:
                    # If it's not a leaf node, recurse
                    recursive_update(matching_original, update_child)

        # Update attributes
        for attr, value in update_element.attrib.items():
            original_element.set(attr, value)

    recursive_update(original_root, update_root)


def xml_to_string(root):
    rough_string = tostring(root, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class XMLGameState:
    def __init__(self, initial_state_file: str):
        self.xml_root_node = self.load_yaml_initial_game_state(initial_state_file)

    def load_yaml_initial_game_state(self, file_path: str):
        return yaml_to_xml(file_path)

    def get_xml_string(self):
        return xml_to_string(self.xml_root_node)

    def update_xml_from_string(self, xml_string: str):
        merge_xml_update(self.xml_root_node, xml_string.replace("\n", ""))

    def save_to_xml_file(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(xml_to_string(self.xml_root_node))

    def load_from_xml_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.xml_root_node = ET.fromstring(file.read())
