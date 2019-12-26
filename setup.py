from setuptools import setup, Command
import datetime
import gettext
import os
import platform
import site


gettext.install('filenamelength', 'filenamelength/locale')


class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.system("rm -Rf build")
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/filenamelength/ --delete-after")
        os.chdir("..")

class Procedure(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
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


class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system()=="Linux":
            os.system("rm -Rf {}/filenamelength*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/filenamelength")
            os.system("rm /usr/share/man/man1/filenamelength.1")
            os.system("rm /usr/share/man/es/man1/filenamelength.1")
        else:
            print(_("Uninstall command only works in Linux"))

class Compile(Command):
    description = "Compile ui and images"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sys import path
        path.append("filenamelength")
        from github import download_from_github
        download_from_github('turulomio','reusingcode','python/decorators.py', 'filenamelength')
        download_from_github('turulomio','reusingcode','python/libmanagers.py', 'filenamelength')
        download_from_github('turulomio','reusingcode','python/github.py', 'filenamelength')
        download_from_github('turulomio','reusingcode','python/datetime_functions.py', 'filenamelength')


class Doc(Command):
    description = "Update man pages and translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #es
        os.system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/filenamelength.pot *.py filenamelength/*.py")
        os.system("msgmerge -N --no-wrap -U locale/es.po locale/filenamelength.pot")
        os.system("msgfmt -cv -o filenamelength/locale/es/LC_MESSAGES/filenamelength.mo locale/es.po")

        for language in ["en", "es"]:
            self.mangenerator(language)

    def mangenerator(self, language):
        """
            Create man pages for parameter language
        """
        from mangenerator import Man
        if language=="en":
            gettext.install('filenamelength', 'badlocale')
            man=Man("man/man1/filenamelength")
        else:
            lang1=gettext.translation('filenamelength', 'filenamelength/locale', languages=[language])
            lang1.install()
            man=Man("man/es/man1/filenamelength")
        print("  - DESCRIPTION in {} is {}".format(language, _("DESCRIPTION")))

        man.setMetadata("filenamelength",  1,   datetime.date.today(), "Mariano Muñoz", _("Admin options to work with the max length of the name of your files"))
        man.setSynopsis("""usage: filenamelength [-h] [--version]
                      [--create_examples | --remove_examples | --minimum MINIMUM]
                      [--order_by_length]""")
        man.header(_("DESCRIPTION"), 1)
        man.paragraph(_("This app has the following mandatory parameters:"), 1)
        man.paragraph("--create_example", 2, True)
        
        man.paragraph(_("With --pretend and --remove you can use this parameters:"), 1)

    ########################################################################

## Version of modele captured from version to avoid problems with package dependencies
__version__= None
with open('filenamelength/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

if platform.system()=="Linux":
    data_files=[('/usr/share/man/man1/', ['man/man1/filenamelength.1']), 
                ('/usr/share/man/es/man1/', ['man/es/man1/filenamelength.1'])
               ]
else:
    data_files=[]

setup(name='filenamelength',
    version=__version__,
    description='Admin options to work with the max length of the name of your files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Programming Language :: Python :: 3',
             ], 
    keywords='remove files datetime patterns',
    url='https://too-many-files.sourceforge.io/',
    author='Turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['filenamelength'],
    entry_points = {'console_scripts': ['filenamelength=filenamelength.filenamelength:main',
                                    ],
                },
    install_requires=['colorama','setuptools'],
    data_files=data_files,
    cmdclass={
    'doxygen': Doxygen,
    'doc': Doc,
    'uninstall':Uninstall,
    'procedure': Procedure,
    'compile': Compile,
         },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
