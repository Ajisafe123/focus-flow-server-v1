import ast
import os
import sys

def get_imports(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            root = ast.parse(f.read(), filename=path)
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            return set()

    imports = set()
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def main():
    requirements = set()
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle package names like 'uvicorn[standard]' or 'bcrypt==3.2.0'
                    pkg = line.split("==")[0].split("[")[0].split(">")[0].split("<")[0].strip().lower()
                    # Map pypi name to import name if different
                    mapping = {
                        "python-jose": "jose",
                        "python-multipart": "multipart", # or python_multipart sometimes but usually not directly imported
                        "python-dotenv": "dotenv",
                        "pydantic-settings": "pydantic_settings",
                        "scikit-learn": "sklearn",
                        "pymongo": "pymongo", # often motor is used
                        "beautifulsoup4": "bs4",
                        "typing_extensions": "typing_extensions",
                        "aiosmtplib": "aiosmtplib",
                        # Add more mappings as needed
                    }
                    requirements.add(mapping.get(pkg, pkg))

    src_imports = set()
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                src_imports.update(get_imports(os.path.join(root, file)))

    # Filter out stdlib (approximate) and internal modules
    stdlib = {
        "os", "sys", "pathlib", "typing", "datetime", "json", "asyncio", "math", "random", "time",
        "email", "uuid", "hashlib", "io", "subprocess", "logging", "re", "shutil", "tempfile",
        "urllib", "functools", "collections", "copy", "enum", "importlib", "inspect", "itertools",
        "operator", "pickle", "platform", "pprint", "socket", "sqlite3", "ssl", "string", "struct",
        "threading", "traceback", "types", "unittest", "weakref", "warnings", "base64", "calendar",
        "contextlib", "csv", "decimal", "doctest", "getpass", "glob", "gzip", "heapq", "hmac", 
        "html", "http", "mimetypes", "numbers", "queue", "secrets", "select", "shelve", "signal",
        "statistics", "tarfile", "textwrap", "token", "tokenize", "unicodedata", "xml", "zipfile",
        "zoneinfo", "abc", "argparse", "ast", "atexit", "bdb", "bisect", "bz2", "cProfile", "cmd",
        "code", "codecs", "compileall", "configparser", "crypt", "ctypes", "curses", "dataclasses",
        "dbm", "difflib", "dis", "distutils", "email", "encodings", "ensurepip", "errno", "faulthandler",
        "fcntl", "filecmp", "fileinput", "fnmatch", "formatter", "fpectl", "fpformat", "fractions",
        "ftplib", "gc", "getopt", "gettext", "glob", "grp", "gzip", "hashlib", "heapq", "hmac", "html",
        "http", "imaplib", "imghdr", "imp", "importlib", "inspect", "io", "ipaddress", "itertools",
        "json", "keyword", "lib2to3", "linecache", "locale", "logging", "lzma", "mailbox", "mailcap",
        "marshmallow", "math", "mimetypes", "mmap", "modulefinder", "msilib", "msvcrt", "multiprocessing",
        "netrc", "nis", "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev", "parser",
        "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform", "plistlib", "poplib",
        "posix", "pprint", "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
        "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched",
        "secrets", "select", "selectors", "shelve", "shlex", "shutil", "signal", "site", "smtpd",
        "smtplib", "sndhdr", "socket", "socketserver", "spwd", "sqlite3", "ssl", "stat", "statistics",
        "string", "stringprep", "struct", "subprocess", "sunau", "symbol", "symtable", "sys", "sysconfig",
        "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "textwrap", "threading",
        "time", "timeit", "tkinter", "token", "tokenize", "trace", "traceback", "tracemalloc", "tty",
        "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest", "urllib", "uu", "uuid",
        "venv", "warnings", "wave", "weakref", "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib",
        "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib"
    }

    # Internal modules start with src
    src_imports = {i for i in src_imports if i != "src" and i not in stdlib}

    print("\n--- Imported Dependencies ---")
    print("\n".join(sorted(src_imports)))

    print("\n--- Unused Requirements (Potential) ---")
    unused = requirements - src_imports
    # Some packages might not be directly imported (e.g. uvicorn, python-multipart, python-dotenv)
    known_indirect = {
        "uvicorn", "multipart", "dotenv", "bcrypt", "pydantic[email]", "passlib", 
        "pymongo", "typing_extensions", "hijri-converter" # maybe hyphen issue?
    }
    
    # Check for hyphens vs underscores mappings I might have missed
    # hijri-converter -> hijri_converter
    
    final_unused = set()
    for u in unused:
        if u not in known_indirect:
            # check if u.replace('-', '_') is in src_imports
            if u.replace('-', '_') in src_imports:
                continue
            final_unused.add(u)
            
    print("\n".join(sorted(final_unused)))

    print("\n--- Missing Requirements (Potential) ---")
    missing = src_imports - requirements
    # Filter out known built-ins or missed mappings
    final_missing = set()
    for m in missing:
         # check if m.replace('_', '-') is in requirements
         if m.replace('_', '-') in requirements:
             continue
         if m in {"bson", "jose", "motor"}: # bson is pymongo, jose is python-jose
             continue
         final_missing.add(m)

    print("\n".join(sorted(final_missing)))

if __name__ == "__main__":
    main()
