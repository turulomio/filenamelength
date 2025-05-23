from datetime import date
from filenamelength import __version__
from gettext import install, translation, gettext
from os import system
from mangenerator import Man

_=gettext



install('filenamelength', 'filenamelength/locale')

def release():
    print(_("New Release:"))
    print(_("  * Change version and date in version.py"))
    print(_("  * Edit Changelog in README"))
    print("  * python setup.py doc")
    print("  * mcedit locale/es.po")
    print("  * python setup.py doc")
    print("  * python setup.py install")
    print("  * python setup.py doxygen")
    print("  * git commit -a -m 'filenamelength-{}'".format(__version__))
    print("  * git push")
    print(_("  * Make a new tag in github"))
    print("  * python setup.py sdist upload -r pypi")
    print("  * python setup.py uninstall")
    print(_("  * Create a new gentoo ebuild with the new version"))
    print(_("  * Upload to portage repository")) 

def translate():
        #es
        system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o filenamelength/locale/filenamelength.pot filenamelength/*.py")
        system("msgmerge -N --no-wrap -U filenamelength/locale/es.po filenamelength/locale/filenamelength.pot")
        system("msgfmt -cv -o filenamelength/locale/es/LC_MESSAGES/filenamelength.mo filenamelength/locale/es.po")
        for language in ["en", "es"]:
            mangenerator(language)

def mangenerator(language):
    """
        Create man pages for parameter language
    """
    if language=="en":
        install('filenamelength', 'badlocale')
        man=Man("man/man1/filenamelength")
    else:
        lang1=translation('filenamelength', 'filenamelength/locale', languages=[language])
        lang1.install()
        man=Man("man/es/man1/filenamelength")
    print("  - DESCRIPTION in {} is {}".format(language, _("DESCRIPTION")))

    man.setMetadata("filenamelength",  1,   date.today(), "Mariano Muñoz", _("Admin options to work with the max length of the name of your files"))
    man.setSynopsis("""usage: filenamelength [-h] [--version]
                    [--create_examples | --remove_examples | --minimum MINIMUM]
                    [--order_by_length]""")
    man.header(_("DESCRIPTION"), 1)
    man.paragraph(_("This app has the following mandatory parameters:"), 1)
    man.paragraph("--create_example", 2, True)
    
    man.paragraph(_("With --pretend and --remove you can use this parameters:"), 1)
