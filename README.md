# MAME Arade Subsystem Organizer

## Overview
This Python script helps users extract and organize arcade subsystems such as SNK NeoGeo or Sega Naomi from a current MAME full romset (non-merged). It automates the creation of subfolders and populates them with the corresponding ROMs and CHDs, facilitating the management of extensive arcade game collections. The script operates by:
- Running ```mame -listxml``` to create an XML file with all supported systems.
- Converting the XML file to a more manageable JSON file.
- Reading the subsystems to be organized from the ArcadeSystems.ini file.
- Creating a subfolder for each subsystem and copying the associated ROMs and CHDs using rsync.

## Installation / Usage

**Step 1:** Clone the repository to your local machine
```bash
git clone https://github.com/b4n4n377/Mame-Arcade-Subsystem-Organizer.git
cd Mame-Arcade-Subsystem-Organizer
```
**Step 2:** Edit the ArcadeSystems.ini file according to your preferences

**Step 3:** Run the script and follow the on-screen instructions

```bash
python main.py
```

