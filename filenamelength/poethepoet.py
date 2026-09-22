from datetime import date
from filenamelength import __version__
from gettext import install, translation, gettext
from multiprocessing import Process
from os import system, chdir, makedirs, path, environ, getcwd
from shutil import which, move, rmtree
from sys import exit, executable

_=gettext

install('filenamelength', 'filenamelength/locale')

def release():
    print(_("New Release:"))
    print("  * Create and issue and its branch in Github. Copy and paste code.")
    print(_("  * Change version and date in __init__.py"))
    print(_("  * Change version in pyproject.toml"))
    print("  * poe translate")
    print("  * mcedit filenamelength/locale/es.po")
    print("  * poe translate")
    print("  * poe video")
    print("  * git commit -a -m 'filenamelength-{}'".format(__version__))
    print("  * git push")
    print(_("  * Make a new tag in github"))
    print("  * poetry build")
    print("  * poetry publish --username --password")
    print(_("  * Create a new gentoo ebuild with the new version"))
    print(_("  * Upload to portage repository")) 

def translate():
    #es
    system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o filenamelength/locale/filenamelength.pot filenamelength/*.py")
    system("msgmerge -N --no-wrap -U filenamelength/locale/es.po filenamelength/locale/filenamelength.pot")
    system("msgfmt -cv -o filenamelength/locale/es/LC_MESSAGES/filenamelength.mo filenamelength/locale/es.po")


def create_examples():
    """Create sample files and directories for VHS recordings."""
    remove_examples()
    makedirs("demo/sub", exist_ok=True)

    with open("demo/short.txt", "w") as f:
        f.write("short\n")

    with open("demo/project_report.pdf", "w") as f:
        f.write("pdf\n")

    with open("demo/financial_audit_report.docx", "w") as f:
        f.write("docx\n")

    with open("demo/archive_records_backup.tar.gz", "w") as f:
        f.write("archive\n")

    with open("demo/sub/longer_path_sample_file.dat", "w") as f:
        f.write("dat\n")


def remove_examples():
    """Remove sample files and directories used for VHS recordings."""
    if path.exists("demo"):
        rmtree("demo")


def generate_command_video(vhs_cmd, root_dir):
    """Generate command.gif using VHS in doc/."""
    doc_dir = path.join(root_dir, "doc")
    system(f"cd '{doc_dir}' && LC_ALL=C.UTF-8 LANG=C.UTF-8 LANGUAGE=en_US:en {vhs_cmd} command.tape")


def generate_howto_video(vhs_cmd, root_dir):
    """Generate howto.gif using VHS in demo/."""
    files_dir = path.join(root_dir, "demo")
    doc_dir = path.join(root_dir, "doc")
    tape_path = path.join(doc_dir, "howto.tape")
    system(f"cd '{files_dir}' && LC_ALL=C.UTF-8 LANG=C.UTF-8 LANGUAGE=en_US:en {vhs_cmd} '{tape_path}'")
    source_gif = path.join(files_dir, "howto.gif")
    dest_gif = path.join(doc_dir, "howto.gif")
    if path.exists(source_gif):
        move(source_gif, dest_gif)


def video():
    """Generate demonstration video recordings and GIFs in parallel using multiprocessing and VHS."""
    # Comprobaciones
    vhs = which("vhs")
    if vhs is None:
        print(_("vhs tool is needed. Look at https://github.com/charmbracelet/vhs"))
        exit(1)

    root_dir = path.abspath(getcwd())

    # Ensure virtualenv bin is in PATH so VHS subshell can run filenamelength
    venv_bin = path.dirname(executable)
    environ["PATH"] = f"{venv_bin}:{environ.get('PATH', '')}"
    environ["LC_ALL"] = "C.UTF-8"
    environ["LANG"] = "C.UTF-8"
    environ["LANGUAGE"] = "en_US:en"

    makedirs("doc", exist_ok=True)

    create_examples()

    # Launch both video generation processes in parallel
    p1 = Process(target=generate_command_video, args=(vhs, root_dir))
    p2 = Process(target=generate_howto_video, args=(vhs, root_dir))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    remove_examples()

    if p1.exitcode != 0 or p2.exitcode != 0:
        print(_("An error occurred during video generation."))
        exit(1)