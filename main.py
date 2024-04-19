import os
import sys
import json
import logging
import subprocess
import configparser
from xml.etree import ElementTree as ET
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MameArcadeSubsystemOrganizer:
    """
    Class to sort MAME ROMs based on a configuration file
    """

    def __init__(
        self, rom_path=None, chd_path=None, xml_path="mame.xml", json_path="mame.json"
    ):
        """
        Constructor to initialize the class with default values
        """
        self.rom_path = rom_path
        self.chd_path = chd_path
        self.xml_path = xml_path
        self.json_path = json_path

    def generate_mame_xml(self):
        """
        Method to generate the MAME XML file
        """
        if os.path.exists(self.xml_path):
            logging.info("XML file already exists. Skipping generation.")
            return True
        logging.info("Generating MAME XML file...")
        return self.execute_command(["mame", "-listxml"], output_file=self.xml_path)

    def convert_xml_to_json(self):
        """
        Method to convert the MAME XML file to JSON
        """
        if os.path.exists(self.json_path):
            logging.info(
                f"JSON file {self.json_path} already exists. Skipping conversion."
            )
            return True
        logging.info("Converting XML to JSON...")
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            machines = []
            for machine in root.findall("machine"):
                machine_dict = {
                    "name": machine.attrib.get("name"),
                    "sourcefile": machine.attrib.get("sourcefile"),
                    "romof": machine.attrib.get("romof", "none"),
                    "cloneof": machine.attrib.get("cloneof", "none"),
                    "ismechanical": machine.attrib.get("ismechanical", "no"),
                    "sampleof": machine.attrib.get("sampleof", "none"),
                    "description": machine.findtext("description", default="none"),
                    "year": machine.findtext("year", default="none"),
                    "manufacturer": machine.findtext("manufacturer", default="none"),
                    "biossets": [
                        {
                            "name": biosset.attrib.get("name"),
                            "description": biosset.attrib.get("description"),
                        }
                        for biosset in machine.findall("biosset")
                    ],
                    "roms": [
                        {
                            "name": rom.attrib.get("name"),
                            "size": rom.attrib.get("size"),
                            "crc": rom.attrib.get("crc"),
                            "sha1": rom.attrib.get("sha1"),
                            "region": rom.attrib.get("region"),
                            "offset": rom.attrib.get("offset"),
                        }
                        for rom in machine.findall("rom")
                    ],
                    "device_refs": [
                        device_ref.attrib.get("name")
                        for device_ref in machine.findall("device_ref")
                    ],
                    "chips": [
                        {
                            "type": chip.attrib.get("type"),
                            "tag": chip.attrib.get("tag"),
                            "name": chip.attrib.get("name"),
                            "clock": chip.attrib.get("clock", "none"),
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
                            "type": feature.attrib.get("type"),
                            "status": feature.attrib.get("status"),
                        }
                        for feature in machine.findall("feature")
                    ],
                }
                machines.append(machine_dict)
            with open(self.json_path, "w") as file:
                json.dump(machines, file, indent=4)
            logging.info("XML successfully converted to JSON.")
            return True
        except ET.ParseError as e:
            logging.error(f"XML parsing error: {e}")
            return False
        except FileNotFoundError:
            logging.error("XML file not found.")
            return False

    def get_user_paths(self):
        """
        Method to get the user paths for ROMs and CHDs
        """
        self.rom_path = prompt(
            "ROM Path: ", completer=PathCompleter(only_directories=True)
        )
        if not os.path.isdir(self.rom_path):
            logging.error("Invalid ROM path.")
            return False
        self.chd_path = prompt(
            "CHD Path: ", completer=PathCompleter(only_directories=True)
        )
        if not os.path.isdir(self.chd_path):
            logging.error("Invalid CHD path.")
            return False
        logging.info("Paths received and validated.")
        return True

    def sort_subsystem_roms(self, config_file="ArcadeSystems.ini"):
        """
        Method to sort the ROMs based on the configuration file
        """
        config = configparser.ConfigParser()
        config.optionxform = str  # preserve case
        config.read(config_file)
        systems = config["Systems"]
        base_dir = os.path.join(
            os.path.dirname(self.rom_path), "Arcade-Systems-filtered"
        )
        os.makedirs(base_dir, exist_ok=True)

        for system, file in systems.items():
            system_dir = os.path.join(base_dir, system)
            os.makedirs(system_dir, exist_ok=True)
            self.copy_roms_and_chds(file, system_dir)

    def copy_roms_and_chds(self, sourcefile, system_dir):
        """
        Method to copy ROMs and CHDs to the system directory
        """
        with open(self.json_path, "r") as json_file:
            machines = json.load(json_file)
            rom_files = [
                os.path.join(self.rom_path, f"{machine['name']}.zip")
                for machine in machines
                if machine["sourcefile"] == sourcefile
                and machine["cloneof"] == "none"
                and os.path.exists(
                    os.path.join(self.rom_path, f"{machine['name']}.zip")
                )
            ]
            chd_folders = [
                os.path.join(self.chd_path, machine["name"])
                for machine in machines
                if machine["sourcefile"] == sourcefile
                and machine["cloneof"] == "none"
                and os.path.isdir(os.path.join(self.chd_path, machine["name"]))
            ]

        if rom_files:
            subprocess.run(["rsync", "-av", "--progress"] + rom_files + [system_dir])
            logging.info(f"ROM files copied to {system_dir} using rsync.")
        else:
            logging.info("No ROM files found to copy.")

        if chd_folders:
            subprocess.run(["rsync", "-av", "--progress"] + chd_folders + [system_dir])
            logging.info(f"CHD folders copied to {system_dir} using rsync.")
        else:
            logging.info("No CHD folders found to copy.")

    def execute_command(self, command, output_file=None):
        """
        Method to execute a command and save the output to a file
        """
        try:
            with open(output_file, "w") as file:
                subprocess.run(
                    command, stdout=file, stderr=subprocess.PIPE, text=True, check=True
                )
            logging.info(
                f"Command '{' '.join(command)}' executed successfully, output saved to {output_file}"
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during command execution: {e.stderr}")
            return False

    def check_aknf_ini_file(self, config_file="aknfList.ini"):
        """
        Helper method for manually checking the validity of the aknfList.ini file
        """
        logging.info("Checking the aknfList.ini file...")
        reference_roms = set()

        # Read ROMs from aknfList.ini file
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(config_file)
        aknfroms = config["AllKillerNoFillerRoms"]

        # Check if the ROMs are present in the MAME JSON
        with open(self.json_path, "r") as json_file:
            machines = json.load(json_file)
            for rom, value in aknfroms.items():
                if value.lower() == "true":
                    found = False
                    for machine in machines:
                        if machine["name"] == rom:
                            found = True
                            # logging.info(f"ROM '{rom}' found in MAME JSON.")

                            # Check dependencies to other ROMs
                            if "device_refs" in machine:
                                device_refs = machine["device_refs"]
                                for device_ref in device_refs:
                                    for machine in machines:
                                        if (
                                            machine["name"] == device_ref
                                            and machine["roms"]
                                        ):
                                            reference_roms.add(device_ref)
                                            break
                            break

                    if not found:
                        logging.warning(
                            f"ROM '{rom}' not found in MAME JSON. Add the successor ROM to aknfList.ini."
                        )

        # Check if the reference ROMs are present aknfList.ini
        if reference_roms:
            # Check if the reference ROMs are present in the aknfroms
            for reference_rom in reference_roms:
                found = False
                for rom, value in aknfroms.items():
                    if reference_rom == rom:
                        found = True
                        break  # Found the reference ROM in aknfList.ini
                if not found:
                    logging.warning(f"ROM '{reference_rom}' not found in aknfList.ini.")

    def sort_aknf_roms(self, config_file="aknfList.ini"):
        """
        Method to sort the ROMs based on the AllKillerNoFiller configuration file
        """
        config = configparser.ConfigParser()
        config.optionxform = str  # preserve case
        config.read(config_file)
        aknf_roms = config["AllKillerNoFillerRoms"]

        base_dir = os.path.join(
            os.path.dirname(self.rom_path), "Arcade-Systems-filtered"
        )
        os.makedirs(base_dir, exist_ok=True)

        system_dir = os.path.join(base_dir, "AllKillerNoFillerRoms")
        os.makedirs(system_dir, exist_ok=True)
        self.copy_aknf_roms_and_chds(aknf_roms, system_dir)

    def copy_aknf_roms_and_chds(self, aknf_roms, system_dir):
        """
        Method to copy specified AKNF ROMs and CHDs to the system directory.
        """

        rom_files = [
            os.path.join(self.rom_path, f"{rom}.zip")
            for rom in aknf_roms
            if os.path.exists(os.path.join(self.rom_path, f"{rom}.zip"))
        ]

        chd_folders = [
            os.path.join(self.chd_path, rom)
            for rom in aknf_roms
            if os.path.isdir(os.path.join(self.chd_path, rom))
        ]

        if rom_files:
            subprocess.run(["rsync", "-av", "--progress"] + rom_files + [system_dir])
            logging.info(f"AKNF ROM files copied to {system_dir} using rsync.")
        else:
            logging.info("No AKNF ROM files found to copy.")

        if chd_folders:
            subprocess.run(["rsync", "-av", "--progress"] + chd_folders + [system_dir])
            logging.info(f"AKNF CHD folders copied to {system_dir} using rsync.")
        else:
            logging.info("No AKNF CHD folders found to copy.")


def main():
    """
    Main function to execute the script
    """
    manager = MameArcadeSubsystemOrganizer(rom_path=None, chd_path=None)

    if not manager.generate_mame_xml():
        sys.exit(1)

    if not manager.convert_xml_to_json():
        sys.exit(1)

    if not manager.get_user_paths():
        sys.exit(1)

    # Uncomment if you want to check the aknfList.ini file
    # manager.check_aknf_ini_file()

    manager.sort_subsystem_roms()

    manager.sort_aknf_roms()


if __name__ == "__main__":
    main()
