"""
Creates a JSON file (modules.json) where keys are EPICS module folder names
(from /cds/group/pcds/epics/R7.0.3.1-2.0/modules) and values are the latest 
version numbers. modules.json is used to update env_vars_versions.json, which 
updates the configure/RELEASE file for every common IOC.
"""

import json
import os
import re

from packaging import version

root = "/cds/group/pcds/epics/R7.0.3.1-2.0/modules"


def compare_versions(ver1, ver2):
    v1 = version.parse(ver1)
    v2 = version.parse(ver2)

    if v1 > v2:
        return ver1
    elif v1 < v2:
        return ver2
    else:
        return "same"


def get_newest_version(folder):
    # Checks in an EPICS module folder and reads its subfolder names
    # (subfolder names use semantic versioning). Returns the latest
    # version.

    dir = root + "/" + folder
    newest = ()
    versions = []

    for ver in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, ver)):
            # Check that 'FAILED' and other chars do not exist in the version
            # name (other than 'R' at the beginning of the string). This
            # assumes that the module version numbers are all in a format
            # similar to 'R3.1.0-1.4.1'.
            if "FAILED" not in ver and not re.search(r"[a-zA-Z]", ver[1:]):
                if "-" in ver:
                    first = ver.split("-")[0][1:]
                    second = ver.split("-")[1]
                    version = (first, second)
                else:
                    version = (ver.split("-")[0][1:],)
                versions.append(version)

    if versions:
        newest = versions.pop(0)
        for current in versions:
            result = compare_versions(newest[0], current[0])
            if result == current[0]:
                newest = current
            elif result == "same":
                # check if both have a second version part
                if len(current) > 1 and len(newest) > 1:
                    result = compare_versions(newest[1], current[1])
                    if result == current[1]:
                        newest = current
                elif len(current) > 1:
                    newest = current

    return newest


def get_module_versions():
    modules_dict = {}

    # Open the modules.json file and load
    with open("modules.json") as file:
        modules_dict = json.load(file)

    # Update modules_dict with the latest version numbers
    for subfolder in os.listdir(root):
        if os.path.isdir(os.path.join(root, subfolder)):
            latest_ver = get_newest_version(subfolder)
            subfolder = subfolder.lower()

            if latest_ver:
                if len(latest_ver) <= 1:
                    num = "".join(latest_ver)
                else:
                    num = "-".join(latest_ver)

                modules_dict[subfolder] = "R" + num

    # write to json file
    with open("modules.json", "w") as outfile:
        json.dump(modules_dict, outfile)
