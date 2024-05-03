import argparse
import json
from xml.etree import ElementTree as ET

def convert_mame_xml_to_json(xml_path, json_path):
    """
    Convert MAME XML data to a structured JSON file.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        machines = []
        for machine in root.findall('machine'):
            machine_dict = {
                "name": machine.get("name"),
                "sourcefile": machine.get("sourcefile"),
                "romof": machine.get("romof", "none"),
                "cloneof": machine.get("cloneof", "none"),
                "ismechanical": machine.get("ismechanical", "no"),
                "sampleof": machine.get("sampleof", "none"),
                "description": machine.findtext("description", default="none"),
                "year": machine.findtext("year", default="none"),
                "manufacturer": machine.findtext("manufacturer", default="none"),
                "biossets": [
                    {
                        "name": biosset.get("name"),
                        "description": biosset.get("description"),
                    }
                    for biosset in machine.findall("biosset")
                ],
                "roms": [
                    {
                        "name": rom.get("name"),
                        "size": rom.get("size"),
                        "crc": rom.get("crc"),
                        "sha1": rom.get("sha1"),
                        "region": rom.get("region"),
                        "offset": rom.get("offset"),
                    }
                    for rom in machine.findall("rom")
                ],
                "device_refs": [
                    device_ref.get("name")
                    for device_ref in machine.findall("device_ref")
                ],
                "chips": [
                    {
                        "type": chip.get("type"),
                        "tag": chip.get("tag"),
                        "name": chip.get("name"),
                        "clock": chip.get("clock", "none"),
                    }
                    for chip in machine.findall("chip")
                ],
                "driver": {
                    "status": machine.findtext("driver/status"),
                    "emulation": machine.findtext("driver/emulation"),
                    "savestate": machine.findtext("driver/savestate"),
                },
                "features": [
                    {
                        "type": feature.get("type"),
                        "status": feature.get("status"),
                    }
                    for feature in machine.findall("feature")
                ],
            }
            machines.append(machine_dict)

        with open(json_path, 'w') as file:
            json.dump(machines, file, indent=4)
        print("XML successfully converted to JSON.")
        return True
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return False
    except FileNotFoundError:
        print("XML or JSON file not found.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MAME XML data to JSON")
    parser.add_argument("input_xml", help="Path to the input XML file")
    parser.add_argument("output_json", help="Path to the output JSON file")
    args = parser.parse_args()
    convert_mame_xml_to_json(args.input_xml, args.output_json)
