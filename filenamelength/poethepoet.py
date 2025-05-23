from datetime import date
from filenamelength import __version__
from gettext import install, translation, gettext
from os import system

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