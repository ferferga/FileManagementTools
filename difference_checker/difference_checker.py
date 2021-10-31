#!/usr/bin/python3
import os
import hashlib
import sqlite3
import shutil
from getpass import getpass
try:
    import progressbar
    progress = True
except ImportError:
    progress = False

dest_folder = ""
orig_folder = ""

def option_chooser():
    while True:
        selection = input("\nYour option ('1' or '2'): ")
        if int(selection) == 1:
            return 1
            break
        elif int(selection) == 2:
            return 2
            break
        else:
            print("That option is invalid")

def check_folder(path):
    return os.path.exists(path)

def format_path(path):
    if path[-1] == "\\" or path[-1] == "/":
        path = path[:-1]
    return path.replace("\\", "/")

def md5(path):
    hash_md5 = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def first_run():
    try:
        os.remove("folder_difference.db")
    except:
        pass
    db_conn = sqlite3.connect("folder_difference.db")
    db = db_conn.cursor()
    db.execute("CREATE TABLE files (path TEXT PRIMARY KEY, md5_before TEXT, md5_after TEXT)")
    db.execute("CREATE TABLE settings (orig_path TEXT PRIMARY KEY)")
    reg = (str(orig_folder),)
    db.execute("INSERT INTO settings VALUES(?)", reg)
    db_conn.commit()
    file_count = 0
    for root, dirs, files in os.walk(orig_folder):
        for name in files:
            file_count += 1
    print("There are " + str(file_count) + " files to check. Processing...\n")
    if progress:
        bar = progressbar.ProgressBar(max_value=file_count)
        loopCount = 0
    for root, dirs, files in os.walk(orig_folder):
        for name in files:
            file_path = format_path(os.path.join(root, name))
            reg = (file_path, md5(file_path), None)
            db.execute("INSERT INTO files VALUES(?,?,?)", reg)
            if progress:
                loopCount +=1
                bar.update(loopCount)
    if progress:
        bar.finish()
    db_conn.commit()
    db.execute("VACUUM")
    db_conn.commit()
    db_conn.close()
    print("First scan done! Do you want to scan for differences now (1) or leave it for another time(2)?")
    option = option_chooser()
    if option == 1:
        second_run()
        return
    else:
        return

def second_run():
    global orig_folder, dest_folder
    db_conn = sqlite3.connect("folder_difference.db")
    db = db_conn.cursor()
    db2 = db_conn.cursor()
    file_array = []
    rowcount = 0
    print("\nChecking if new files were added after the first scan...")
    db.execute("SELECT * FROM settings")
    orig_folder = db.fetchone()[0]
    if check_folder(orig_folder):
        for root, dirs, files in os.walk(orig_folder):
            for name in files:
                file_array.append(format_path(os.path.join(root, name)))
        db.execute("SELECT path FROM files")
        for row in db:
            rowcount += 1
            if row[0] in file_array:
                file_array.remove(row[0])

        print()
        if len(file_array) != 0:
            print(str(len(file_array)) + " files were added.")
            print("Checking first the differences of the files found in the first scan...")
        else:
            print("No files added. Checking differences...")

        if progress:
            bar = progressbar.ProgressBar(max_value=rowcount)
            loopCount = 0
        db.execute("SELECT * FROM files")
        for row in db:
            reg = (md5(row[0]), row[0], row[1])
            db2.execute("UPDATE files SET md5_after = ? WHERE path = ? AND md5_before = ?", reg)
            if progress:
                loopCount += 1
                bar.update(loopCount)

        if progress:
            bar.finish()

        if len(file_array) != 0:
            print("\nCalculating MD5Sum of the new files...")
            if progress:
                bar = progressbar.ProgressBar(max_value=len(file_array))
            for index, file in enumerate(file_array):
                reg = (file, None, md5(file))
                db.execute("INSERT INTO files VALUES(?,?,?)", reg)
                if progress:
                    bar.update(index)
            if progress:
                bar.finish()
        db_conn.commit()
        print("Difference checking done!\n\n")

        while True:
            dest_folder = format_path(input("Where do you want to copy the changed files?: "))
            if check_folder(dest_folder):
                break
            else:
                print("Invalid path. Please, try again (make sure that it it's created first).")

        print()
        print()
        print("Copying files to the directory...")

        basepath = format_path(os.path.basename(orig_folder))
        if os.path.exists(format_path(os.path.join(dest_folder, basepath))):
            shutil.rmtree(format_path(os.path.join(dest_folder, basepath)), True)
        os.mkdir(format_path(os.path.join(dest_folder, basepath)))

        db.execute("SELECT path FROM files WHERE (md5_before != md5_after) OR md5_before IS NULL AND md5_after IS NOT NULL")
        for row in db:
            path = row[0]
            path = row[0][row[0].find(basepath):]

            if not os.path.exists(format_path(os.path.join(dest_folder, os.path.dirname(path)))):
                os.makedirs(format_path(os.path.join(dest_folder, os.path.dirname(path))))

            shutil.copy(row[0], format_path(os.path.join(dest_folder, os.path.dirname(path), os.path.basename(path))))

        db.execute("SELECT COUNT(path) FROM files WHERE md5_after IS NULL")
        if db.fetchone()[0] != 0:
            with open(dest_folder + "/deleted.txt", "w+") as f:
                f.write("These files were deleted:\n\n")
                db.execute("SELECT path FROM files WHERE md5_after IS NULL")
                for row in db:
                    f.write(row[0])

        db_conn.commit()
        db_conn.close()
        getpass("\n\nDone! Thanks for using! Press ENTER to exit")
    else:
        print("The original folder that was used for scanning wasn't found. Exiting...")
        return

def setup():
    global orig_folder
    print("This is the first time you run this. Type the path of the folder do you want to calculate")
    while True:
        orig_folder = format_path(input("Folder to calculate: "))
        if check_folder(orig_folder):
            print()
            break
        else:
            print("Invalid path, please try again (make sure that the folder exists)")
    first_run()

print("Welcome to the 'folder difference checker' tool.")
print("This tool will scan one folder two times and copy all the changed files that took place between those two scans in that folder to another directory.\n\n")

if os.path.isfile("folder_difference.db"):
    print("You already scanned a folder. Do you want to copy the changed files to another folder (1) or start from scratch (2)?")
    option = option_chooser()
    if option == 1:
        second_run()
    else:
        setup()
else:
    setup()
