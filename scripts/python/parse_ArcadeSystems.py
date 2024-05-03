import json
import argparse
import sys

def parse_ini_file(ini_file):
    systems = []
    with open(ini_file, 'r') as file:
        for line in file:
            if not line.strip().startswith('#') and line.strip():
                parts = line.split('=')
                if len(parts) == 2:
                    systems.append({"name": parts[0].strip(), "driver": parts[1].strip()})
    return systems

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse INI file to extract arcade systems")
    parser.add_argument('ini_file', help='Path to the INI file containing arcade systems')
    args = parser.parse_args()

    systems = parse_ini_file(args.ini_file)
    print(json.dumps(systems, indent=4))  # This ensures output is in proper JSON format
