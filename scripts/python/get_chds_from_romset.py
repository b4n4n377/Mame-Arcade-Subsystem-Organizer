import os
import argparse

def check_chdpath_for_romset(romset_file, chdpath):
    # Ensure the ROM set file exists
    if not os.path.isfile(romset_file):
        print("The ROM set file does not exist.")
        return []

    # Ensure the CHD path directory exists
    if not os.path.isdir(chdpath):
        print("The CHD path directory does not exist.")
        return []

    valid_roms = []
    with open(romset_file, 'r') as file:
        for rom_name in file:
            rom_name = rom_name.strip()
            chd_dir = os.path.join(chdpath, rom_name)
            if os.path.isdir(chd_dir):
                valid_roms.append(rom_name)

    return valid_roms

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check which ROM sets have a corresponding CHD directory.")
    parser.add_argument('romset_file', help='Path to the ROM set file containing the list of ROM names.')
    parser.add_argument('chdpath', help='Path to the directory containing CHD folders.')
    args = parser.parse_args()

    found_roms = check_chdpath_for_romset(args.romset_file, args.chdpath)
    for rom in found_roms:
        print(rom)
