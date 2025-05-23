from datetime import date
from filenamelength import __version__
from gettext import install, translation, gettext
from os import system

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