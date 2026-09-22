from datetime import date
from filenamelength import __version__
from gettext import install, translation, gettext
from os import system, chdir, makedirs, path, environ
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
    makedirs("filenamelength_examples/files/subfolder/deep/path", exist_ok=True)

    with open("filenamelength_examples/files/short.txt", "w") as f:
        f.write("short file content\n")

    with open("filenamelength_examples/files/project_financial_report_2026.pdf", "w") as f:
        f.write("pdf content\n")

    with open("filenamelength_examples/files/very_long_descriptive_document_name_for_backup.docx", "w") as f:
        f.write("docx content\n")

    with open("filenamelength_examples/files/extraordinarily_long_archive_file_name_exceeding_standard_limits.tar.gz", "w") as f:
        f.write("archive content\n")

    with open("filenamelength_examples/files/subfolder/deep/path/nested_file_with_a_long_full_path_specification.dat", "w") as f:
        f.write("dat content\n")


def remove_examples():
    """Remove sample files and directories used for VHS recordings."""
    if path.exists("filenamelength_examples"):
        rmtree("filenamelength_examples")


def video():
    """Generate demonstration video recordings and GIFs using VHS."""
    # Comprobaciones
    vhs = which("vhs")
    if vhs is None:
        print(_("vhs tool is needed. Look at https://github.com/charmbracelet/vhs"))
        exit(1)

    # Ensure virtualenv bin is in PATH so VHS subshell can run filenamelength
    venv_bin = path.dirname(executable)
    environ["PATH"] = f"{venv_bin}:{environ.get('PATH', '')}"

    makedirs("doc", exist_ok=True)

    chdir("doc")
    system(f"{vhs} command.tape")
    chdir("..")

    create_examples()
    chdir("filenamelength_examples/files")
    system(f"{vhs} ../../doc/howto.tape")
    move("howto.gif", "../../doc/howto.gif")
    chdir("../..")
    remove_examples()