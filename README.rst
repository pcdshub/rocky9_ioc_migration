===============================
rocky9_ioc_migration
===============================

.. image:: https://github.com/pcdshub/rocky9_ioc_migration/actions/workflows/standard.yml/badge.svg
        :target: https://github.com/pcdshub/rocky9_ioc_migration/actions/workflows/standard.yml

.. image:: https://img.shields.io/pypi/v/rocky9_ioc_migration.svg
        :target: https://pypi.python.org/pypi/rocky9_ioc_migration


`Documentation <https://pcdshub.github.io/rocky9_ioc_migration/>`_

A collection of scripts for migrating IOC repos from RHEL7 to Rocky 9. Most of the steps have been automated. Several manual updates will be needed and are described in the 'Instructions' section below. The scripts can be reused for future efforts to migrate to a newer server.

Requirements
------------

* Python 3.9+

Instructions
------------

::

1. In your working directory create a folder called ``iocs``.

2. Git fork the Rocky 9 IOC Migration repo from https://github.com/pcdshub/rocky9_ioc_migration. Git clone the fork in ``/iocs``. The new directory structure should be ``<your working directory>/iocs/rocky9_ioc_migration``.

3. Navigate to ``/iocs/rocky9_ioc_migration/rocky9_ioc_migration`` and run ``ioc_fork_all.sh`` to git fork all common IOC repos. You may need to run this script multiple times until all 150+ repos have been forked. This is due to restrictions imposed by Github for how quickly a user can fork a large number of repos.

4. From ``/iocs/rocky9_ioc_migration/rocky9_ioc_migration`` run ``ioc_clone_all.sh`` to git clone all the forked repos into ``/iocs``.

5. Navigate to ``/iocs/rocky9_ioc_migration/rocky9_ioc_migration``, open ``main.py``, and update the global variable ``epics_base_version`` with the new version number. Also update ``epics_site_top`` and ``pspkg_root`` if needed.

6. Once all repos have been cloned run ``python main.py``. This will grab the latest EPICS module version numbers from ``/cds/group/pcds/epics/R7.0.3.1-2.0/modules`` and update every IOC's ``configure/RELEASE`` file with the latest version numbers. It will also update each IOC's ``RELEASE_SITE`` files. EPICS modules loosely follow the semantic versioning system.

7. Check the new server's IOC build status page to determine which module environmental variables will need to be manually updated (for Rocky 9 it's at https://confluence.slac.stanford.edu/pages/viewpage.action?spaceKey=PCDS&title=PCDS%20Rocky%209%20Build%20Status). For example, the current version of EPICS uses version R2.15-1.0.2 of the ipac module and not R3.0.0-1.1.5 (the latest version number). Open the file ``module_version_exceptions.json`` located in ``/iocs/rocky9_ioc_migration/rocky9_ioc_migration``. Add or update any exceptions to current module versions.

8. (Optional) I found this step to be useful for managing the top 15 most commonly used IOCs. From inside ``/iocs`` create a new folder called ``manual_updates``. Move the top 15 most commonly used IOCs into ``manual_updates``. The top 15 are ``ioc-common-ads-ioc, ioc-common-aerotech, ioc-common-bk-1697, ioc-common-epixMon, ioc-common-evr, ioc-common-gigECam, ioc-common-ict, ioc-common-ims, ioc-common-pdu_snmp, ioc-common-pvNotepad, ioc-common-qmini, ioc-common-smaract, ioc-common-thorlabs-ell, ioc-common-tprStandalone`` (various motor records and leviton IOCs are also commonly used but it wasn't feasible to test them in the Makerspace for this migration).

Some of the top 15 common IOCs, such as ``ioc-common-ads-ioc`` and ``ioc-common-gigECam``, use a different set of EPICS module version numbers and will need to be manually updated.

9. If TID releases new module versions, navigate to ``/iocs/rocky9_ioc_migration/rocky9_ioc_migration`` and run ``python main.py`` again to update all IOCs.


Running the Tests
-----------------

Each top 15 common IOC should be tested on the new development server before it's tested on the test host in Makerspace. Test IOCs already exist for most of the top 15 and are located in the IOC's ``children`` folder.