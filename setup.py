from setuptools import setup, find_packages
#
## requirements are in "requirements.txt"
reqs = sorted(set(map(lambda line: line.strip(),
                      filter(lambda line: len( line.strip( ) ) != 0,
                             open( 'requirements.txt', 'r').readlines()))))
setup(
    name = 'nprstuff',
    version = '1.0',
    #
    ## following advice on find_packages excluding tests from https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages
    packages = find_packages( exclude = ["*.tests", "*.tests.*", "tests" ] ),
    # package_dir = { "": "nprstuff" },
    url = 'https://github.com/tanimislam/nprstuff',
    license = 'BSD-2-Clause',
    author = 'Tanim Islam',
    author_email = 'tanim.islam@gmail.com',
    description = 'I like NPR, so I made some scripts to download my favorite programs from NPR.',
    #
    ## classification: where in package space does "nprstuff live"?
    ## follow (poorly) advice I infer from https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-setup-script
    classifiers=[
    # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Programming Language :: Python :: 3',
    # uncomment if you test on these interpreters:
    # 'Programming Language :: Python :: Implementation :: IronPython',
    # 'Programming Language :: Python :: Implementation :: Jython',
    # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
        'Topic :: Multimedia',
    ],
    #
    ## requirements
    install_requires = reqs,
    python_requires = '>=3',
    #
    ## the executables I am creating
    entry_points = {
        'console_scripts' : [
            "music_to_m4a = nprstuff.cli.music_to_m4a:_main",
            "freshair = nprstuff.cli.freshair:_freshair",
            "freshair_crontab = nprstuff.cli.freshair:_freshair_crontab",
            "freshair_by_year = nprstuff.cli.freshair:_freshair_by_year",
            "freshair_fix_crontab = nprstuff.cli.freshair:_freshair_fix_crontab",
            "github_md_2_html = nprstuff.cli.github_md_2_html:_main",
            "autoCropImage = nprstuff.cli.autoCropImage:_main",
            "convertImage = nprstuff.cli.convertImage:_main",
            "changedates = nprstuff.cli.changedates:_main",
            "display = nprstuff.cli.display:_main",
            "download_surahs = nprstuff.cli.download_surahs:_main",
            "imageFromURL = nprstuff.cli.imageFromURL:_main",
            "thisamericanlife = nprstuff.cli.thisamericanlife:_main",
            "thisamericanlife_crontab = nprstuff.core.thisamericanlife:thisamericanlife_crontab",
            "waitwait = nprstuff.cli.waitwait:_waitwait",
            "waitwait_crontab = nprstuff.core.waitwait:waitwait_crontab",
            "waitwait_by_year = nprstuff.cli.waitwait:_waitwait_by_year",
        ]
    }
)
