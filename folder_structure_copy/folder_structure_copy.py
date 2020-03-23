#!/usr/bin/python3
import os

def check_folder(path):
    return os.path.exists(path)

def format_path(path):
    if path[-1] == "\\" or path[-1] == "/":
        path = path[:-1]
    return path.replace("\\", "/")

while True:
    try:
        orig_folder = format_path(input("Type the path of the folder whose structure do you want to replicate: "))
        dest_folder = format_path(input("Type the path where do you want to replicate the folder structure: "))
        if check_folder(orig_folder) and check_folder(dest_folder):
            print("Working... Might take a while in large directories")
            for root, dirs, files in os.walk(orig_folder):
                for name in dirs:
                    if not os.path.exists(dest_folder + format_path(os.path.join(root, name)).replace(orig_folder, "")):
                        os.mkdir(dest_folder + format_path(os.path.join(root, name)).replace(orig_folder, ""))
            print("\n'" + orig_folder + "' structure replicated!")
        else:
            print("The given path doesn't exist or contains an slash at the end, try again")
        print()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("There was an error: " + str(e) + "\nTry it again!\n")
