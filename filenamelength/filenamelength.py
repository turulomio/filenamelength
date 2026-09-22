from colorama import init, Style
from argparse import ArgumentParser, RawTextHelpFormatter
from filenamelength.__init__ import __version__, __versiondate__
from gettext import translation
import json
from os import sep, getcwd, makedirs, path, walk, rename, listdir, environ, name as os_name
from datetime import datetime
from importlib.resources import files
from pydicts import lod
from shutil import rmtree
from sys import exit
from io import StringIO
from contextlib import redirect_stdout
from filenamelength.filesystems import get_fsinfo_lod

##Seriously, generally speaking it is 252 characters, but that comes with caveats. In real-world, common usage, the max is 247. Here is why:
##1. The maximum Windows filename length to the operating system is 260 characters, however that includes a number of required characters that lower the effective number.
##2. From the 260, you must allow room for the following:
##    Drive letter
##    Colon after drive letter
##    Backslash after drive letter
##    End-of-Line character
##    Backslashes that are part of the filename path (e.g. c:\dir-name\dir-name\filename)
##So, that takes the 260 down to 256 characters as an absolute maximum. That would be the case only if you had a very long filename with no extension and it was located on the root folder of the disk.
##3. Looking at more common and realistic scenarios, your effective maximum is going to be significantly lower. Add an extension (very common), and your maximum length drops to 252 or 251 characters, depending on the length of the extension (most are 3 characters; some are 4 - e.g. docx or mpeg).
##4. Each directory name in the path of the filename must be included in that 260 characters. This is why errors sometimes occur when moving files between directories. Users are often confused by the "filename too long" message when they see a short filename. The reason for the error is the total path length must conform to the filename maximum length. Windows makes no distinction in filename storage between the path and filenames. They are stored in the same space. Linux OTOH, does make a distinction. On a Linux O.S., your path name is maxxed out at 4,096 characters while the filename is limited to 256.
##Breaking down all of the above:
##Absolute (relative) maximum file length - including path - is 256 characters.
##That is how you should be thinking of filename length in Windows - as path length and not file name length. Since there is no way to know how long the path of the directory your file is in, I can't give you a firm answer. Do your files all have extensions? I don't know that either.
##If you will not know ahead of time if the file has an extension name or not, presume it will use up 5 characters for an extension and that will lower your path max to 251. If the files won't be stored in the root disk folder, make sure you allow room for the directory path names and backslash characters that separate each directory name. That will take you down to 248 (and probably lower).
##This process is one of many reasons why Windows architecture is antiquated - even in Windows 10

try:
    t=translation('filenamelength', files("filenamelength") / 'locale')
    _=t.gettext
except:
    _=str


def get_user_config_dir():
    """
    Returns the absolute path to the user configuration directory for filenamelength.

    Resolves XDG_CONFIG_HOME if defined, %APPDATA% on Windows, or ~/.config on Unix-like systems.
    The directory is created if it does not already exist.

    :return: Absolute path to the user configuration directory.
    :rtype: str
    """
    if "XDG_CONFIG_HOME" in environ and environ["XDG_CONFIG_HOME"]:
        base_dir = environ["XDG_CONFIG_HOME"]
    elif os_name == "nt":
        base_dir = environ.get("APPDATA", path.expanduser("~"))
    else:
        base_dir = path.join(path.expanduser("~"), ".config")
    config_dir = path.join(base_dir, "filenamelength")
    makedirs(config_dir, exist_ok=True)
    return config_dir


def ensure_user_config():
    """
    Ensures that the user configuration directory and required configuration files exist.

    Creates 'config.json' with default settings (such as max_history_entries) and
    'history.json' (empty list) if they do not exist.

    :return: Absolute path to the user configuration directory.
    :rtype: str
    """
    config_dir = get_user_config_dir()
    config_file = path.join(config_dir, "config.json")
    if not path.exists(config_file):
        default_config = {
            "max_history_entries": 100
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
            f.write("\n")
    history_file = path.join(config_dir, "history.json")
    if not path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
            f.write("\n")
    return config_dir


def get_config():
    """
    Loads and returns the user configuration dictionary from 'config.json'.

    Falls back to default configuration values if the file cannot be read or parsed.

    :return: Dictionary containing configuration options.
    :rtype: dict
    """
    config_dir = ensure_user_config()
    config_file = path.join(config_dir, "config.json")
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"max_history_entries": 100}


def load_history():
    """
    Loads the rename history sessions from 'history.json'.

    :return: List of history session dictionaries, each containing timestamp, cwd, and operations.
    :rtype: list
    """
    config_dir = ensure_user_config()
    history_file = path.join(config_dir, "history.json")
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_history(history):
    """
    Persists the rename history sessions to 'history.json', trimming older entries
    if the list exceeds 'max_history_entries' defined in configuration.

    :param history: List of history session dictionaries to save.
    :type history: list
    """
    config_dir = ensure_user_config()
    history_file = path.join(config_dir, "history.json")
    config = get_config()
    max_entries = config.get("max_history_entries", 100)
    if len(history) > max_entries:
        history = history[-max_entries:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
        f.write("\n")



def generate_optimized_filename(filename, target_len, existing_names):
    """
    Generates an optimized filename truncated to at most target_len characters
    while preserving the file extension and resolving collisions.

    If candidate filename collides with any entry in existing_names, increments
    a numbered suffix (_1, _2, ...) and shortens the stem accordingly to guarantee
    the total length does not exceed target_len.

    :param filename: Original filename to optimize.
    :type filename: str
    :param target_len: Desired maximum length for the filename.
    :type target_len: int
    :param existing_names: Set of filenames already present or planned in the directory.
    :type existing_names: set
    :return: An optimized filename of length <= target_len that is not in existing_names.
    :rtype: str
    """
    if len(filename) <= target_len and filename not in existing_names:
        return filename

    stem, ext = path.splitext(filename)

    if target_len > len(ext):
        allowed_stem = target_len - len(ext)
        candidate = stem[:allowed_stem] + ext
    else:
        candidate = filename[:target_len]

    if candidate not in existing_names:
        return candidate

    counter = 1
    while True:
        num_str = f"_{counter}"
        needed = len(num_str) + len(ext)
        if target_len >= needed:
            allowed_stem = target_len - needed
            candidate = stem[:allowed_stem] + num_str + ext
        elif target_len >= len(num_str):
            allowed = target_len - len(num_str)
            candidate = (stem + ext)[:allowed] + num_str
        else:
            candidate = num_str[:target_len]

        if candidate not in existing_names:
            return candidate
        counter += 1


def rename_files(lod_files, minimum_path_length, minimum_filename_length):
    """
    Renames files in lod_files that exceed length limits to optimized names.

    Calculates target filename length based on minimum_filename_length and/or
    minimum_path_length without modifying directory paths. Avoids overwriting
    existing files by appending numbering on collision. Records successful
    operations to user history for undo support.

    :param lod_files: List of file dictionaries (with 'Path', 'Path length', 'Filename length').
    :type lod_files: list
    :param minimum_path_length: Target maximum path length threshold (0 if disabled).
    :type minimum_path_length: int
    :param minimum_filename_length: Target maximum filename length threshold (0 if disabled).
    :type minimum_filename_length: int
    :return: List of performed rename operations, each containing 'original' and 'renamed' paths.
    :rtype: list
    """
    operations = []
    assigned_by_dir = {}

    for item in lod_files:
        file_path = item["Path"]
        if not path.exists(file_path):
            continue

        dirpath = path.dirname(file_path)
        filename = path.basename(file_path)
        dir_len = len(dirpath) + len(sep)

        limits = []
        if minimum_filename_length > 0:
            limits.append(minimum_filename_length)
        if minimum_path_length > 0:
            limits.append(minimum_path_length - dir_len)

        if not limits:
            continue

        target_fn_len = min(limits)

        if target_fn_len <= 0:
            print(Style.BRIGHT + _("Cannot rename '{}': directory path length ({}) already exceeds or equals desired path length ({}).").format(file_path, dir_len, minimum_path_length) + Style.RESET_ALL)
            continue

        if len(filename) <= target_fn_len:
            continue

        if dirpath not in assigned_by_dir:
            try:
                assigned_by_dir[dirpath] = set(listdir(dirpath))
            except Exception:
                assigned_by_dir[dirpath] = set()

        existing_names = assigned_by_dir[dirpath].copy()
        if filename in existing_names:
            existing_names.remove(filename)

        new_filename = generate_optimized_filename(filename, target_fn_len, existing_names)

        if new_filename == filename:
            continue

        new_file_path = path.join(dirpath, new_filename)
        try:
            rename(file_path, new_file_path)
            assigned_by_dir[dirpath].add(new_filename)
            operations.append({
                "original": file_path,
                "renamed": new_file_path
            })
        except Exception as e:
            print(Style.BRIGHT + _("Error renaming '{}' to '{}': {}").format(file_path, new_file_path, e) + Style.RESET_ALL)

    if operations:
        history = load_history()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "cwd": getcwd(),
            "operations": operations
        })
        save_history(history)

        lod_renamed = [
            {
                _("Original path"): op["original"],
                _("New path"): op["renamed"],
                _("New filename length"): len(path.basename(op["renamed"])),
                _("New path length"): len(op["renamed"])
            }
            for op in operations
        ]
        print()
        print(Style.BRIGHT + _("Renamed files:") + Style.RESET_ALL)
        lod.lod_print(lod_renamed)
        print(Style.BRIGHT + _("{} files renamed.").format(len(operations)) + Style.RESET_ALL)
    else:
        print(Style.BRIGHT + _("No files needed to be renamed.") + Style.RESET_ALL)

    return operations


def undo_rename(steps=1):
    """
    Undoes the last N rename sessions from user history in reverse order.

    Restores renamed files to their original paths. Checks that original destinations
    are not overwritten if they were recreated. Updates the user history file.

    :param steps: Number of rename sessions to undo (defaults to 1).
    :type steps: int
    :return: Total number of files successfully restored.
    :rtype: int
    """
    ensure_user_config()
    history = load_history()
    if not history:
        print(Style.BRIGHT + _("No rename operations to undo.") + Style.RESET_ALL)
        return 0

    if steps <= 0:
        steps = 1

    num_to_undo = min(steps, len(history))
    total_undone = 0

    for step_idx in range(num_to_undo):
        session = history.pop()
        operations = session.get("operations", [])
        undone_in_step = []

        for op in reversed(operations):
            original = op["original"]
            renamed = op["renamed"]

            if not path.exists(renamed):
                print(Style.BRIGHT + _("Cannot undo: '{}' not found.").format(renamed) + Style.RESET_ALL)
                continue
            if path.exists(original) and original != renamed:
                print(Style.BRIGHT + _("Cannot undo: '{}' already exists.").format(original) + Style.RESET_ALL)
                continue
            try:
                rename(renamed, original)
                undone_in_step.append({
                    _("Current path"): renamed,
                    _("Restored path"): original
                })
                total_undone += 1
            except Exception as e:
                print(Style.BRIGHT + _("Error restoring '{}' to '{}': {}").format(renamed, original, e) + Style.RESET_ALL)

        if undone_in_step:
            print()
            print(Style.BRIGHT + _("Undone rename operations (session {}):").format(step_idx + 1) + Style.RESET_ALL)
            lod.lod_print(undone_in_step)

    save_history(history)
    print(Style.BRIGHT + _("{} total files restored across {} session(s).").format(total_undone, num_to_undo) + Style.RESET_ALL)
    return total_undone


def create_lod_files(directory):
    """
    Recursively scans the given directory and returns a list of dictionaries with file metadata.

    :param directory: Root directory path to scan.
    :type directory: str
    :raises Exception: If directory is None.
    :return: List of dictionaries with 'Path', 'Path length', and 'Filename length'.
    :rtype: list
    """
    r=[]
    if directory!=None:
        for currentpath, folders, files in walk(directory):
            for file in files:
                file_path=path.abspath(currentpath + sep + file)
                r.append({
                    "Path": file_path,
                    "Path length": len(file_path),
                    "Filename length": len(file)
                })
    else:
        raise Exception(_("Directory error"))
    return r 


def print_lod_files(lod_files, minimum_path_length, minimum_filename_length, order_by):
    """
    Filters, sorts, and prints the list of file dictionaries as a formatted table.

    :param lod_files: List of file dictionaries to filter and display.
    :type lod_files: list
    :param minimum_path_length: Filter threshold for path length (>= value).
    :type minimum_path_length: int
    :param minimum_filename_length: Filter threshold for filename length (>= value).
    :type minimum_filename_length: int
    :param order_by: Sorting criterion ('Path', 'PathLength', or 'FilenameLength').
    :type order_by: str
    :return: Filtered list of file dictionaries.
    :rtype: list
    """
    lod_files=lod.lod_filter_dictionaries(lod_files,lambda d, index: d["Filename length"]>=minimum_filename_length and d["Path length"]>=minimum_path_length)
    if order_by=="Path":
        lod_files=lod.lod_order_by(lod_files,"Path")
        suf=_("ordered by path")
    elif order_by=="PathLength":
        lod_files=lod.lod_order_by(lod_files,"Path length")
        suf=_("ordered by path length")
    elif order_by=="FilenameLength":
        lod_files=lod.lod_order_by(lod_files,"Filename length")
        suf=_("ordered by filename length")
    lod.lod_print(lod_files)
    print (Style.BRIGHT + _("{} files found {}, whose path length is greater than or equal to {} and its filename length is greater than or equal to {}".format(len(lod_files), suf, minimum_path_length, minimum_filename_length))+Style.RESET_ALL)
    return lod_files


## filenamelength main script
## If arguments is None, launches with sys.argc parameters. Entry point is filenamelength:main
## You can call with main(['--pretend']). It's equivalento to os.system('filenamelength --pretend')
## @param arguments is an array with parser arguments. For example: ['--max_files_to_store','9']. 
def main(arguments=None):
    """
    Main CLI entry point for filenamelength.

    Parses command line arguments, handles listing, renaming, and undo operations.

    :param arguments: Command-line arguments list (defaults to None, reading sys.argv).
    :type arguments: list or None
    :return: Exit status code (0 on success, non-zero on error).
    :rtype: int
    """

    ensure_user_config()
    epilog_buffer = StringIO()
    with redirect_stdout(epilog_buffer):
        lod.lod_print(get_fsinfo_lod())
    epilog_text = (
        _("The table below shows the maximum filename and path length limits for common filesystems:")
        + "\n\n"
        + epilog_buffer.getvalue()
        + "\n"
        + _("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year))
    )
    parser=ArgumentParser(prog='filenamelength', description=_('Lists files with path and filename conditions'), epilog=epilog_text, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--minimum_path_length', help=_("List files whose path length is greater than or equal to this value"), action="store", default=0, type=int)
    parser.add_argument('--minimum_filename_length', help=_("List files whose filename length is greater than or equal to this value"), action="store", default=0, type=int)
    parser.add_argument("--order_by", choices=['Path', 'PathLength', 'FilenameLength'], help=_("Different ways to order output"), default="Path")
    parser.add_argument('--rename', action='store_true', help=_("Rename files exceeding limits to an optimized name within the desired length"))
    parser.add_argument('--undo', nargs='?', const=1, type=int, default=None, help=_("Undo the last N rename operations (default: 1)"))
    args=parser.parse_args(arguments)

    init(autoreset=True)

    if args.undo is not None:
        if args.rename:
            print(Style.BRIGHT + _("Error: Cannot use --rename and --undo together.") + Style.RESET_ALL)
            return 1
        if args.undo <= 0:
            print(Style.BRIGHT + _("Error: --undo value must be greater than 0.") + Style.RESET_ALL)
            return 1
        undo_rename(steps=args.undo)
        return 0

    if args.rename and args.minimum_path_length == 0 and args.minimum_filename_length == 0:
        print(Style.BRIGHT + _("Error: --rename requires --minimum_path_length or --minimum_filename_length to be set.") + Style.RESET_ALL)
        return 1

    lod_files=create_lod_files(getcwd())
    filtered_lod = print_lod_files(lod_files, args.minimum_path_length, args.minimum_filename_length, args.order_by)

    if args.rename:
        rename_files(filtered_lod, args.minimum_path_length, args.minimum_filename_length)

    return 0
