# File Management Tools

Under this repository I will publish some of my scripts for simplifying some tasks while managing files and folders. They were written in
Python 3.8 (so make sure you're using Python > 3.8 before reporting any problem) and used exclusively on Windows at the moment (should work
as well in POSIX systems, though, although not tested).

Those are made for getting the job done as quick as possible, so they're far from perfect.

# Description of the tools

## Folder structure copy

This script will copy, recursively, the folder structure of a folder into another one, ignoring files. It's like ``shutil.copytree``.

## Difference checker

This tool will copy the modified files from a folder into another folder. Detailed explanation:
* First, the tool will scan and calculate the MD5 checksum of each of the files.
* Once it finishes, you can close the tool (or leave it open) and do some modifications to the files contained in that folder
* You can now do the second scan. On it, the program will check which files were changed and will copy the modified ones to a folder of your choice (output's folder).

New files will also be copied. Deleted files will be written to a ``deleted.txt`` file in the output's folder root.

# How to run them

I've built binaries for **Windows 64 bits** and **Linux (amd64 and armhf)**,
which can be found in the [Releases tab](https://github.com/ferferga/FileManagementTools/releases), so you don't have to install Python or any requirements.

For other architectures and systems, the general procedure to run this is to download Python > 3.6, clone this repository and install the requirements. One-line:

``sudo apt install -y python3 python3-pip && git clone https://github.com/ferferga/FileManagementTools && cd FileManagementTools && python3 <program_to_run>``

# License

This is licensed as GPL3, so all the derivatives from this work must be open source as well. Any contribution is welcome!