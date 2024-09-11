import xml.etree.ElementTree as ET
import json
import os

OUTPUT_DIR = "out"
CONFIG_XML = os.path.join(OUTPUT_DIR, "config.xml")
META_JSON = os.path.join(OUTPUT_DIR, "meta.json")

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    classes = {}
    aggregations = []

    for element in root:
        if element.tag == "Class":
            class_name = element.get("name")
            is_root = element.get("isRoot", "false") == "true"
            documentation = element.get("documentation", "")
            attributes = [
                {"name": attr.get("name"), "type": attr.get("type")}
                for attr in element.findall("Attribute")
            ]
            classes[class_name] = {
                "name": class_name,
                "isRoot": is_root,
                "documentation": documentation,
                "attributes": attributes
            }
        elif element.tag == "Aggregation":
            aggregations.append({
                "source": element.get("source"),
                "target": element.get("target"),
                "sourceMultiplicity": element.get("sourceMultiplicity"),
                "targetMultiplicity": element.get("targetMultiplicity")
            })
    return classes, aggregations

# Генерация файла config.xml
def generate_config_xml(classes, aggregations):
    bts = ET.Element("BTS")
    for attr in classes["BTS"]["attributes"]:
        ET.SubElement(bts, attr["name"]).text = attr["type"]

    for agg in aggregations:
        if agg["target"] == "BTS":
            target_elem = ET.SubElement(bts, agg["source"])
            if agg["source"] in classes:
                for attr in classes[agg["source"]]["attributes"]:
                    ET.SubElement(target_elem, attr["name"]).text = attr["type"]

    tree = ET.ElementTree(bts)
    tree.write(CONFIG_XML, encoding="utf-8", xml_declaration=True)

def generate_meta_json(classes, aggregations):
    meta = []
    for class_name, class_info in classes.items():
        meta_entry = {
            "class": class_name,
            "documentation": class_info["documentation"],
            "isRoot": class_info["isRoot"],
            "parameters": class_info["attributes"]
        }
        for agg in aggregations:
            if agg["target"] == class_name:
                meta_entry["parameters"].append({"name": agg["source"], "type": "class"})
                meta_entry["min"] = agg["sourceMultiplicity"].split("..")[0] if ".." in agg["sourceMultiplicity"] else agg["sourceMultiplicity"]
                meta_entry["max"] = agg["sourceMultiplicity"].split("..")[-1] if ".." in agg["sourceMultiplicity"] else agg["sourceMultiplicity"]
        meta.append(meta_entry)

    with open(META_JSON, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4)

def main():
    ensure_output_dir()
    classes, aggregations = parse_xml("test_input.xml")
    generate_config_xml(classes, aggregations)
    generate_meta_json(classes, aggregations)
    print(f"Файлы {CONFIG_XML} и {META_JSON} успешно сгенерированы.")

if __name__ == "__main__":
    main()
