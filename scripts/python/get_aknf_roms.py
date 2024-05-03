import configparser
import argparse

def parse_ini_file(ini_file):
    """Parse the INI file and print enabled ROMs."""
    config = configparser.ConfigParser()
    config.read(ini_file)

    for key in config['AllKillerNoFillerRoms']:
        if config.getboolean('AllKillerNoFillerRoms', key):
            print(key)

def main():
    parser = argparse.ArgumentParser(description='Parse enabled ROMs from a given INI file.')
    parser.add_argument('ini_file', type=str, help='Path to the INI file containing ROM settings.')
    args = parser.parse_args()

    parse_ini_file(args.ini_file)

if __name__ == "__main__":
    main()
