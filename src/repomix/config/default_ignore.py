"""
Default Ignore Module - Define Default Ignore Patterns
"""

# Default list of ignored files and directories
default_ignore_list = [
    # Version Control
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    "_darcs",
    ".fossil",
    "CVS",
    # IDEs and Editors
    ".idea",
    ".vscode",
    "*.swp",
    "*.swo",
    "*~",
    "*.bak",
    ".project",
    ".settings",
    ".classpath",
    ".factorypath",
    "*.sublime-*",
    ".vs",
    # Build Outputs
    "build",
    "dist",
    "out",
    "target",
    "*.pyc",
    "__pycache__",
    "*.class",
    "*.o",
    "*.obj",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.lib",
    "*.a",
    # Dependency Directories
    "node_modules",
    "bower_components",
    "vendor",
    ".venv",
    "venv",
    "env",
    ".env",
    ".tox",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    # Package Managers
    "*.egg",
    "*.egg-info",
    "*.whl",
    "pip-log.txt",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "package-lock.json",
    "yarn.lock",
    "Pipfile.lock",
    "poetry.lock",
    # Documentation and Media
    "docs/_build",
    "site",
    "*.pdf",
    "*.doc",
    "*.docx",
    "*.ppt",
    "*.pptx",
    "*.xls",
    "*.xlsx",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.ico",
    "*.svg",
    "*.mp3",
    "*.mp4",
    "*.avi",
    "*.mov",
    # System Files
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    # Temporary Files
    "*.tmp",
    "*.temp",
    "*.log",
    "*.pid",
    "*.cache",
    # Security Related
    "*.key",
    "*.pem",
    "*.cert",
    "*.crt",
    "*.p12",
    "*.pfx",
    "*.jks",
    "*.keystore",
    # Compressed Files
    "*.zip",
    "*.rar",
    "*.7z",
    "*.gz",
    "*.tar",
    "*.tgz",
    # Data Files
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.mdb",
    "*.csv",
    # Others
    ".repomix-output.*",
    ".repomixignore",
    "repomix.config.json",
    # Byte-compiled / optimized / DLL files
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    # C extensions
    "*.so",
    # Distribution / packaging
    ".Python",
    "build/",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    ".eggs/",
    "lib/",
    "lib64/",
    "parts/",
    "sdist/",
    "var/",
    "wheels/",
    "share/python-wheels/",
    "*.egg-info/",
    ".installed.cfg",
    "*.egg",
    "MANIFEST",
    # PyInstaller
    #  Usually these files are written by a python script from a template
    #  before PyInstaller builds the exe, so as to inject date/other infos into it.
    "*.manifest",
    "*.spec",
    # Installer logs
    "pip-log.txt",
    "pip-delete-this-directory.txt",
    # Unit test / coverage reports
    "htmlcov/",
    ".tox/",
    ".nox/",
    ".coverage",
    ".coverage.*",
    ".cache",
    "nosetests.xml",
    "coverage.xml",
    "*.cover",
    "*.py,cover",
    ".hypothesis/",
    ".pytest_cache/",
    "cover/",
    # Translations
    "*.mo",
    "*.pot",
    # Django stuff:
    "*.log",
    "local_settings.py",
    "db.sqlite3",
    "db.sqlite3-journal",
    # Flask stuff:
    "instance/",
    ".webassets-cache",
    # Scrapy stuff:
    ".scrapy",
    # Sphinx documentation
    "docs/_build/",
    # PyBuilder
    ".pybuilder/",
    "target/",
    # Jupyter Notebook
    ".ipynb_checkpoints",
    # IPython
    "profile_default/",
    "ipython_config.py",
    # pyenv
    #   For a library or package, you might want to ignore these files since the code is
    #   intended to run in multiple environments; otherwise, check them in:
    # .python-version
    # pipenv
    #   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
    #   However, in case of collaboration, if having platform-specific dependencies or dependencies
    #   having no cross-platform support, pipenv may install dependencies that don't work, or not
    #   install all needed dependencies.
    # Pipfile.lock
    # poetry
    #   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
    #   This is especially recommended for binary packages to ensure reproducibility, and is more
    #   commonly ignored for libraries.
    #   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
    # poetry.lock
    # pdm
    #   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
    # pdm.lock
    #   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
    #   in version control.
    #   https://pdm-project.org/#use-with-ide
    ".pdm.toml",
    ".pdm-python",
    ".pdm-build/",
    # PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
    "__pypackages__/",
    # Celery stuff
    "celerybeat-schedule",
    "celerybeat.pid",
    # SageMath parsed files
    "*.sage.py",
    # Environments
    ".env",
    ".venv",
    "env/",
    "venv/",
    "ENV/",
    "env.bak/",
    "venv.bak/",
    # Spyder project settings
    ".spyderproject",
    ".spyproject",
    # Rope project settings
    ".ropeproject",
    # mkdocs documentation
    "/site",
    # mypy
    ".mypy_cache/",
    ".dmypy.json",
    "dmypy.json",
    # Pyre type checker
    ".pyre/",
    # pytype static type analyzer
    ".pytype/",
    # Cython debug symbols
    "cython_debug/",
]
