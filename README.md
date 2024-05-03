# MAME Arade Subsystem Organizer

## Overview
This **(now ansible)** script helps users extract and organize arcade subsystems such as SNK NeoGeo or Sega Naomi from a current MAME full romset (non-merged). It automates the creation of subfolders and populates them with the corresponding ROMs and CHDs, facilitating the management of extensive arcade game collections. 

**Update 04/2024:** It now also creates a sub folder with all the games of the 'All Killer No Filler' list, see http://forum.arcadecontrols.com/index.php?topic=149708.0

**Update 05/2024:** Adapted the whole script to ansible, so it can be run remotely, for example on your MAME computer.


The script operates by:
- Running ```mame -listxml``` to create an XML file with all supported systems.
- Converting the XML file to a more manageable JSON file.
- Reading the subsystems to be organized from the ArcadeSystems.ini file.
- Creating a subfolder for each subsystem and copying the associated ROMs and CHDs using rsync.

## Installation / Usage

**Step 0:** Install ansible to your local machine, e.g. in arch linux
```bash
sudo pacman -Sy ansible
```

**Step 1:** Clone the repository to your local machine
```bash
git clone https://github.com/b4n4n377/Mame-Arcade-Subsystem-Organizer.git
cd Mame-Arcade-Subsystem-Organizer
```
**Step 2:** Edit the ArcadeSystems.ini file according to your preferences

**Step 3:** Edit the ansible inventory file config/inventory.yml to your remote host where the romsets are at

**Step 3:** Run the script

```bash
./run-playbook.sh
```

