import json
import argparse
import sys

def filter_mame_json_by_criteria(json_file, sourcefile):
    """Filter the MAME JSON file for machines matching a specific sourcefile and having 'cloneof' set to 'none'.
       Also include device references that exist as standalone machines and have non-empty roms."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Create a dictionary mapping machine names to their data for quick access
        all_machines = {machine['name']: machine for machine in data}

        # Filter machines based on sourcefile and cloneof criteria
        filtered_machines = {
            machine['name']: machine
            for machine in data
            if machine.get('sourcefile', '') == sourcefile and machine.get('cloneof', '') == 'none'
        }

        # Collect additional devices as standalone machines that have non-empty roms
        additional_machines = {}
        for name, machine in filtered_machines.items():
            device_refs = machine.get('device_refs', [])
            for device in device_refs:
                if device in all_machines and device not in filtered_machines and device not in additional_machines:
                    device_machine = all_machines[device]
                    if device_machine.get('roms', []):  # Check if 'roms' list is not empty
                        additional_machines[device] = device_machine

        # Combine results
        combined_results = list(filtered_machines.values()) + list(additional_machines.values())

        # Format the results to only include the name field
        result_list = [{"name": machine["name"]} for machine in combined_results]

    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {json_file}"}))
        sys.exit(1)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON format"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    
    return result_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter MAME machines by source file and clone status, including relevant devices with ROMs.")
    parser.add_argument('json_file', help='Path to the MAME JSON file')
    parser.add_argument('sourcefile', help='Source file to match, e.g., "capcom/cps2.cpp"')
    args = parser.parse_args()

    filtered_machines = filter_mame_json_by_criteria(args.json_file, args.sourcefile)
    print(json.dumps(filtered_machines, indent=4))
