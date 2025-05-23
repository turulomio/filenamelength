from colorama import init, Style
from argparse import ArgumentParser, RawTextHelpFormatter
from filenamelength.__init__ import __version__, __versiondate__
from gettext import translation
from os import sep, getcwd, makedirs,  path, walk
from importlib.resources import files
from pydicts import lod
from shutil import rmtree
from sys import exit

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


def create_lod_files(directory):
    r=[]
    if directory!=None:
        for currentpath, folders, files in walk('.'):
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
                

## filenamelength main script
## If arguments is None, launches with sys.argc parameters. Entry point is filenamelength:main
## You can call with main(['--pretend']). It's equivalento to os.system('filenamelength --pretend')
## @param arguments is an array with parser arguments. For example: ['--max_files_to_store','9']. 
def main(arguments=None):
    parser=ArgumentParser(prog='filenamelength', description=_('Lists files with path and filename conditions'), epilog=_("Minimum length for windows is 247")+"\n\n"+_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--minimum_path_length', help=_("List files whose path length is greater than or equal to this value"), action="store", default=0, type=int)
    parser.add_argument('--minimum_filename_length', help=_("List files whose filename length is greater than or equal to this value"), action="store", default=0, type=int)
    parser.add_argument("--order_by", choices=['Path', 'PathLength', 'FilenameLength'], help=_("Different ways to order output"), default="Path")
    args=parser.parse_args(arguments)

    init(autoreset=True)

    lod_files=create_lod_files(getcwd())
    print_lod_files(lod_files, args.minimum_path_length, args.minimum_filename_length, args.order_by)
