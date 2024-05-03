#!/bin/bash

# 1) Edit config/inventory.yml to match your remote host

# 2) Edit config/ArcadeSystems.ini to select the mame subsystems you want to sort

# 3) Run the playbook
ansible-playbook scripts/ansible/playbook.yml -i config/inventory.yml