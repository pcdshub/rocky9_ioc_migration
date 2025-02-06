"""
This script goes into the configure/RELEASE file of every common IOC folder
and sets module environmental variables to the latest EPICS module
version number found in /cds/group/pcds/epics/R7.0.3.1-2.0/modules.

Examples:
FFMPEGSERVER_MODULE_VERSION = R2.1.1-2.2.2
HISTORY_MODULE_VERSION = R2.7.0
IOCADMIN_MODULE_VERSION = R3.1.16-1.4.0

This script also updates BASE_MODULE_VERSION, EPICS_SITE_TOP, and PSPKG_ROOT
in RELEASE_SITE.

Note that ioc-common-ads-ioc and ioc-common-gigECam are configured differently
from other common IOCs. They may use older EPICS module versions and should be
updated by hand. Check the PCDS Rocky 9 Build Status Confluence page for the
right versions to use.
"""

import json
import os
import subprocess
from get_module_versions import get_module_versions


# Environmental variable settings for RELEASE_SITE. Update these variables
# when migrating to a new server.
epics_base_version = "R7.0.3.1-2.0"
epics_site_top = "/cds/group/pcds/epics"
pspkg_root = "/cds/group/pcds/pkg_mgr"

iocs_config_release = []
iocs_release_site = []
env_var_dict = {}
modules_dict = {}
modules_set = set()


def create_ioc_lists():
    global iocs_config_release
    global iocs_release_site
    global modules_set

    parent = os.path.dirname(os.path.join(os.path.dirname(__file__), ""))
    grandparent = os.path.dirname(parent)
    greatgrandparent = os.path.dirname(grandparent)

    # Create lists of IOCs that have configure/RELEASE and RELEASE_SITE files
    for item in os.listdir(greatgrandparent):
        if os.path.isdir(os.path.join(greatgrandparent, item)) and "__" not in item:
            file_config_release = greatgrandparent + "/" + item + "/configure/RELEASE"
            file_release_site = greatgrandparent + "/" + item + "/RELEASE_SITE"

            if os.path.exists(file_config_release):
                iocs_config_release.append(file_config_release)

            if os.path.exists(file_release_site):
                iocs_release_site.append(file_release_site)

    # Look through all configure/RELEASE files and create a set of module
    # environmental variables.
    for filepath in iocs_config_release:
        if os.path.isfile(filepath):
            with open(filepath, "r+") as file:
                for line in file:
                    newline = line.replace("\t", "").strip()
                    newline = "".join(newline.split(" "))

                    if "_MODULE_VERSION=" in newline and not line.startswith("#"):
                        mod_name = newline.split("=")[0]
                        # put into a set to avoid duplicates
                        modules_set.add(mod_name.strip())


def update_configure_release_file():
    global env_var_dict
    global modules_dict

    # Contains module environmental variables and their latest version numbers
    with open("env_vars_versions.json") as file:
        env_var_dict = json.load(file)

    # Contains EPICS module folder names and their latest version numbers
    with open("modules.json") as file:
        modules_dict = json.load(file)

    # ########################################################################
    # This section contains module environmental variables whose names do not
    # correspond exactly to an EPICS module folder name, so their values are
    # hardcoded.
    # ########################################################################
    env_var_dict["ETHERCAT_MODULE_VERSION"] = modules_dict["ethercatmc"]
    env_var_dict["NORMATIVETYPES_MODULE_VERSION"] = modules_dict["normativetypescpp"]
    env_var_dict["BLD_CLIENT_MODULE_VERSION"] = modules_dict["bldclient"]
    env_var_dict["PVDATA_MODULE_VERSION"] = modules_dict["pvdatacpp"]
    env_var_dict["PVACCESS_MODULE_VERSION"] = modules_dict["pvaccesscpp"]
    env_var_dict["TIMING_API_MODULE_VERSION"] = modules_dict["timingapi"]
    env_var_dict["DIAG_TIMER_MODULE_VERSION"] = modules_dict["diagtimer"]

    # ########################################################################
    # EPICS modules loosely follow semantic versionining. This section
    # contains module environmental variables that use a different number than
    # the latest version number for the current build of EPICS base. Check the
    # tables in the PCDS Rocky 9 Build Status Confluence page for the correct
    # version number to use.
    # ########################################################################
    env_var_dict["STREAMDEVICE_MODULE_VERSION"] = "R2.8.9-1.2.2"
    env_var_dict["STREAM_MODULE_VERSION"] = "R2.8.9-1.2.2"
    env_var_dict["IPAC_MODULE_VERSION"] = "R2.15-1.0.2"

    # Update the remaining environmental variables with the latest module
    # version numbers
    for key in modules_set:
        env_var_lower = (key.split("_MODULE_VERSION")[0]).lower()

        try:
            env_var_dict[key] = modules_dict[env_var_lower]
        except KeyError:
            if not env_var_dict[key]:
                env_var_dict[key] = ""
                print(
                    f"Unable to find a module version number for '{key}'. It may be obsolete/no longer used or the EPICS module folder name may be spelled differently."
                )

    with open("env_vars_versions.json", "w") as outfile:
        json.dump(env_var_dict, outfile)

    # Update configure/RELEASE files all common IOCs
    for filepath in iocs_config_release:
        if os.path.isfile(filepath):
            with open(filepath, "r") as file:
                data = file.readlines()
                newdata = []

                for line in data:
                    newline = line.replace("\t", "").strip()
                    newline = "".join(newline.split(" "))

                    if "_MODULE_VERSION=" in newline and not line.startswith("#"):
                        env_var = newline.split("=")[0]
                        version = newline.split("=")[1]
                        if env_var_dict[env_var]:
                            version = env_var_dict[env_var]
                        newline = env_var + " = " + version
                        newdata.append(newline.strip())
                    else:
                        newdata.append(line.strip())

            with open(filepath, "w") as outfile:
                for line in newdata:
                    outfile.write(line + "\n")


def update_release_site_file():
    # Update BASE_MODULE_VERSION, EPICS_SITE_TOP, and PSPKG_ROOT
    for filepath in iocs_release_site:
        if os.path.isfile(filepath):
            with open(filepath, "r+") as file:
                data = file.readlines()
                newdata = []
                base_mod_ver = False

                for line in data:
                    newline = line.replace("\t", "").strip()
                    newline = "".join(newline.split(" "))

                    if "BASE_MODULE_VERSION=" in newline and not line.startswith("#"):
                        newline = "BASE_MODULE_VERSION = " + epics_base_version
                        newdata.append(newline.strip())
                        base_mod_ver = True
                    elif "EPICS_SITE_TOP=" in newline and not line.startswith("#"):
                        newline = "EPICS_SITE_TOP = " + epics_site_top
                        newdata.append(newline.strip())
                    elif "EPICS_MODULES=" in newline:
                        if base_mod_ver:
                            newline = "EPICS_MODULES = $(EPICS_SITE_TOP)/$(BASE_MODULE_VERSION)/modules"
                            newdata.append(newline.strip())
                        else:
                            new1 = "BASE_MODULE_VERSION = " + epics_base_version
                            new2 = "EPICS_MODULES = $(EPICS_SITE_TOP)/$(BASE_MODULE_VERSION)/modules"
                            newdata.append(new1.strip())
                            newdata.append(new2.strip())
                        base_mod_ver = False

                    elif "PSPKG_ROOT=" in newline and not line.startswith("#"):
                        newline = "PSPKG_ROOT = " + pspkg_root
                        newdata.append(newline.strip())
                    else:
                        newdata.append(line.strip())

            with open(filepath, "w") as outfile:
                for line in newdata:
                    outfile.write(line + "\n")


def main():
    get_module_versions()
    create_ioc_lists()
    update_configure_release_file()
    update_release_site_file()


if __name__ == "__main__":
    main()
    # subprocess.call('ioc_git_commit.sh')  # creates a new branch, adds, commits, pushes, opens PR
