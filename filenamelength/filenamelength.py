from colorama import init, Style
from datetime import datetime, timedelta
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
    def __init__(self, directory):
        ObjectManager.__init__(self)
        self.__pretending=1# Tag to set if we are using pretending or not. Can take None: Nor remove nor pretend, 0 Remove, 1 Pretend
            
        for currentpath, folders, files in walk('.'):
            for file in files:
                self.append(Filename(path.abspath(currentpath + sep + file)))

    def print(self):
        self.order_by_length()
        for  o in self.arr:
            print("{} {}".format(o.length(), o.filename))


    #This function must be called after set status
    def __write_log(self, ):
        s=self.__header_string() + "\n"
        for o in self.arr:
                 s=s+"{} >>> {}\n".format(o.filename, _("Delete"))
        f=open("filenamelength.log","a")
        f.write(s)
        f.close()



    def order_by_length(self):       
        self.arr=sorted(self.arr, key=lambda e: e.length(),  reverse=False) 

    #This function must be called after set status
    def __console_output(self):
#        print(self.__header_string(color=True))
#        if self.length()==0:
#            return
#
#        print (self.one_line_status())
#
#        n_remain=self.__number_files_with_status(FileStatus.Remain)
#        n_delete=self.__number_files_with_status(FileStatus.Delete)
#        n_young=self.__number_files_with_status(FileStatus.TooYoungToDelete)
#        n_over=self.__number_files_with_status(FileStatus.OverMaxFiles)
#        if self.__pretending==1:
#            if self.__all_filenames_are_directories():
#                print (_("Directories status pretending:"))
#            elif self.__all_filenames_are_regular_files():
#                print (_("File status pretending:"))
#            result=_("So, {} files will be deleted and {} will be kept when you use --remove parameter.").format(Fore.YELLOW + str(n_delete+n_over) + Style.RESET_ALL, Fore.YELLOW + str(n_remain+n_young) +Style.RESET_ALL)
#        elif self.__pretending==0:
#            if self.__all_filenames_are_directories():
#                print (_("Directories status removing:"))
#            elif self.__all_filenames_are_regular_files():
#                print (_("File status removing:"))
#            result=_("So, {} files have been deleted and {} files have been kept.").format(Fore.YELLOW + str(n_delete+n_over) + Style.RESET_ALL, Fore.YELLOW + str(n_remain+n_young) +Style.RESET_ALL)
#        print ("  * {} [{}]: {}".format(_("Remains"), Fore.GREEN + _("R") + Style.RESET_ALL, n_remain))
#        print ("  * {} [{}]: {}".format(_("Delete"), Fore.RED + _("D") + Style.RESET_ALL, n_delete))
#        print ("  * {} [{}]: {}".format(_("Too young to delete"), Fore.MAGENTA + _("Y") + Style.RESET_ALL, n_young))
#        print ("  * {} [{}]: {}".format(_("Over max files"), Fore.YELLOW + _("O") + Style.RESET_ALL, n_over))
        print("")


    ## Shows information in console
    def pretend(self):
        self.__pretending=1
        self.__set_filename_status()
        self.__console_output()

    ## Shows information in console
    ## Write log
    ## Delete Files
    def remove(self):
        self.__pretending=0
#        self.__set_filename_status()
#        self.__console_output()
#        if self.logging==True:
#            self.__write_log()
#        for o in self.arr:
#            if o.status in [FileStatus.OverMaxFiles, FileStatus.Delete]:
#                if os.path.isfile(o.filename):
#                    os.remove(o.filename)
#                elif os.path.isdir(o.filename):
#                    shutil.rmtree(o.filename)


#def makedirs(dir):
#    try:
#       os.makedirs(dir)
#    except:
#       pass





## Creates an example subdirectory and fills it with datetime pattern filenames
def create_examples():
    makedirs("filenamelength_examples/files")
    number=1000
    for i in range (number):
        d=datetime.now()-timedelta(days=i)
        filename="filenamelength_examples/files/{}{:02d}{:02d} {:02d}{:02d} filenamelength example.txt".format(d.year,d.month,d.day,d.hour,d.minute)
        f=open(filename,"w")
        f.close()

    makedirs("filenamelength_examples/directories")
    number=1000
    for i in range (number):
        d=datetime.now()-timedelta(days=i)
        filename="filenamelength_examples/directories/{}{:02d}{:02d} {:02d}{:02d} Directory/filenamelength example.txt".format(d.year,d.month,d.day,d.hour,d.minute)
        makedirs(path.dirname(filename))        
        f=open(filename,"w")
        f.close()

    makedirs("filenamelength_examples/files_with_different_roots")
    number=5
    for i in range (number):
        d=datetime.now()-timedelta(days=i)
        filename="filenamelength_examples/files_with_different_roots/{}{:02d}{:02d} {:02d}{:02d} filenamelength example {}.txt".format(d.year,d.month,d.day,d.hour,d.minute, i)
        f=open(filename,"w")
        f.close()


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
    parser=ArgumentParser(prog='filenamelength', description=_('Admin options to work with the max length of the name of your files'), epilog=_("Developed by Mariano Muñoz 2019-{}".format(__versiondate__.year)), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)

    group= parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--create_examples', help=_("Create example directories"), action="store_true",default=False)
    group.add_argument('--remove_examples', help=_("Remove example directories'"), action="store_true",default=False)
    group.add_argument('--to_windows', help=_("Removes files permanently"), action="store_true", default=False)
    group.add_argument('--pretend', help=_("Makes a simulation and doesn't remove files"), action="store_true", default=False)

    args=parser.parse_args(arguments)

    init(autoreset=True)

    if args.create_examples==True:
        create_examples()
        exit(ExitCodes.Success)
    if args.remove_examples==True:
        remove_examples()
        exit(ExitCodes.Success)

    manager=FilenameManager(getcwd())

    if args.pretend==True:
        manager.pretend()

    manager.print()
    # List files
