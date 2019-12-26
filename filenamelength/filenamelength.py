from colorama import init, Style
from argparse import ArgumentParser, RawTextHelpFormatter
from filenamelength.libmanagers import ObjectManager
from filenamelength.version import __version__, __versiondate__
from gettext import translation
from os import sep, getcwd, makedirs,  path, walk
from pkg_resources import resource_filename
from shutil import rmtree
from sys import exit
try:
    t=translation('filenamelength',resource_filename("filenamelength","locale"))
    _=t.gettext
except:
    _=str


class ExitCodes:
    Success=0
    MixedRoots=1
    MixedFilesDirectories=2
    NotDeveloped=3
    ArgumentError=4
    
    ##Younger files parameter bigger than max number of files
    YoungGTMax=5


class Filename:
    def __init__(self, filename):
        self.filename=filename

    def __repr__(self):
        return("FWD: {}".format(self.filename))
        
    def lengthDirectory(self):
        pass
        
    def lengthBasename(self):
        pass
        
    def length(self):
        return len (self.filename)
## Only extracts files in current directory
## This object has two itineraries 
## 1. Pretend. Show information in console
## 2. Write. Show information in console. Writes log. Delete innecesary files.
class FilenameManager(ObjectManager):
    ## @param directory If None creates an empty manager
    def __init__(self, directory=None):
        ObjectManager.__init__(self)
        self.__pretending=1# Tag to set if we are using pretending or not. Can take None: Nor remove nor pretend, 0 Remove, 1 Pretend
            
        if directory!=None:
            for currentpath, folders, files in walk('.'):
                for file in files:
                    self.append(Filename(path.abspath(currentpath + sep + file)))

    def print(self, order_by_length=False):
        if order_by_length==False:
            self.order_by_name()
            suf="ordered by name"
        else:
            self.order_by_length()
            suf="ordered by length"
        errors=0
        print (Style.BRIGHT + _("FilenameLength list")+Style.RESET_ALL)
        for  o in self.arr:
            try:
                print("  + {} {}".format(o.length(), o.filename))
            except:
                print(Style.BRIGHT+"  + Error with a filename"+Style.RESET_ALL)
                errors=errors+1
        print (Style.BRIGHT + _("{} files found {}".format(self.length(), suf))+Style.RESET_ALL)
                

    def FilenameManager_length_minimum(self, minimum):  #This function must be called after set status
        r=FilenameManager()
        for o in self.arr:
            if o.length()>=minimum:
                r.append(o)
        return r

    def order_by_length(self):       
        self.arr=sorted(self.arr, key=lambda e: e.length(),  reverse=False) 

    def order_by_name(self):       
        self.arr=sorted(self.arr, key=lambda e: e.filename,  reverse=False) 


## Creates an example subdirectory and fills it with datetime pattern filenames
def create_examples():
    makedirs("filenamelength_examples", exist_ok=True)
    s="1234567890"
    try:
        for i in range (1, 100):
            filename=s*i
            f=open("filenamelength_examples"+ sep + filename,"w")
            f.close()
    except:
        print( "Error with filename length: ,", len(filename))
    print (Style.BRIGHT + _("Different examples have been created in the directory 'filenamelength_examples'"))

def remove_examples():
    if path.exists('filenamelength_examples'):
        rmtree('filenamelength_examples')
        print (_("'filenamelength_examples' directory removed"))
    else:
        print (_("I can't remove 'filenamelength_examples' directory"))


## filenamelength main script
## If arguments is None, launches with sys.argc parameters. Entry point is filenamelength:main
## You can call with main(['--pretend']). It's equivalento to os.system('filenamelength --pretend')
## @param arguments is an array with parser arguments. For example: ['--max_files_to_store','9']. 
def main(arguments=None):
    parser=ArgumentParser(prog='filenamelength', description=_('Admin options to work with the max length of the name of your files'), epilog=_("Minimum length for windows is 247")+"\n\n"+_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)

    group= parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--create_examples', help=_("Create example directories"), action="store_true",default=False)
    group.add_argument('--remove_examples', help=_("Remove example directories'"), action="store_true",default=False)
#    group.add_argument('--to_windows', help=_("Removes files permanently"), action="store_true", default=False)
#    group.add_argument('--pretend', help=_("Makes a simulation and doesn't remove files"), action="store_true", default=False)
    group.add_argument('--minimum', help=_("List files with a minimum length"), action="store")


    parser.add_argument('--order_by_length', action='store_true', default=False)
    args=parser.parse_args(arguments)

    init(autoreset=True)

    if args.create_examples==True:
        create_examples()
        exit(ExitCodes.Success)
    if args.remove_examples==True:
        remove_examples()
        exit(ExitCodes.Success)

    manager=FilenameManager(getcwd())
        
    if args.minimum:
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
        args.minimum=int(args.minimum)
        incompatible=manager.FilenameManager_length_minimum(args.minimum)
        incompatible.print(args.order_by_length)
        print("Files with a minimum length of {}".format(args.minimum))
        exit(ExitCodes.Success)

    manager.print(args.order_by_length)
    # List files
