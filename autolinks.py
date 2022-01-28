import json
import os
import re
import logging
import argparse


img_pattern = re.compile(r"^<img(?:\s.*)?\ssrc\s*=\s*\"([^\"]*)\".*>$")  # pattern for image markdown in notebook
path_pattern = re.compile(r"https://edunet\.kea\.su/repo/(EduNet-(?:(?:content)|(?:web_dependencies))/(L\d+)/.+\..+)")  # pattern for image path
lpattern = re.compile(r"(L\d+)(_\w*)?\.ipynb")  # lecture filename pattern


parser = argparse.ArgumentParser()
parser.add_argument("--diskpath", help="Path to disk on your computer", default="Z:")
parser.add_argument("--logfile", help="Path to log file", default="links.log")
parser.add_argument("--repopath", help="Path to repo on disk (from disk root)", default="Sites/edunet.kea.su/repo")
parser.add_argument("--path", help="Path to notebooks with lectures", default="out")
parser.add_argument("--append", help="Append previous log", default=False, action="store_true")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("[%(levelname)s] [%(asctime)s] %(name)s: %(message)s")
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)
logger.addHandler(sh)


def get_lecture_links(path):
    with open(path, encoding="utf-8") as f:
        lecture = json.load(f)
    if "cells" not in lecture:
        logger.warning(f"File ({path}) incorrect!")
        return []
    links = []
    for i, cell in enumerate(lecture["cells"]):
        if cell["cell_type"] != "markdown":
            continue
        for src in cell["source"]:
            match = img_pattern.match(src)
            if not match:
                continue
            link = match.group(1)
            match = path_pattern.match(link)
            if match:
                links.append((True, link, match.group(1), match.group(2)))
            else:
                links.append((False, link, None, None))
    return links


def get_disk_links(relpath):
    links = set()
    abspath = os.path.join(REPO_PATH, relpath)
    try:
        for filename in os.listdir(abspath):
            links.add(os.path.join(relpath, filename))
    except FileNotFoundError:
        logger.warning(f"Can't get disk links from {abspath}")
    return links


def check_lecture(path, lecture_code, logfile):
    disk_links = get_disk_links(os.path.join(CONTENT_DIR_NAME, lecture_code, "img_license"))
    disk_links = disk_links | get_disk_links(os.path.join(DEP_DIR_NAME, lecture_code))

    lecture_links = get_lecture_links(path)

    unsupported = set()
    incorrect_code = set()
    not_on_disk = set()
    existing = set()

    for supported, link, ref, code in lecture_links:
        if not supported:
            unsupported.add(link)
            continue
        if code != lecture_code:
            incorrect_code.add(link)
            continue

        if ref not in disk_links:
            not_on_disk.add(link)
        
        existing.add(ref)

    not_used = set()

    for link in disk_links:
        if link not in existing:
            not_used.add(link)

    with open(logfile, "a") as f:
        print(f"Lecture {lecture_code}:", file=f)
        print("\tNot used:", file=f)
        for link in not_used:
            print(f"\t\t- {link}", file=f)
        print("\tNot on disk:", file=f)
        for link in not_on_disk:
            print(f"\t\t- {link}", file=f)
        print("\tIncorrect code:", file=f)
        for link in incorrect_code:
            print(f"\t\t- {link}", file=f)
        print("\tUnsupported source:", file=f)
        for link in unsupported:
            print(f"\t\t- {link}", file=f)
        print("\n", file=f)


if __name__ == "__main__":
    args = parser.parse_args()

    CONTENT_DIR_NAME = "EduNet-content"
    DEP_DIR_NAME = "EduNet-web_dependencies"
    REPO_PATH = os.path.join(args.diskpath, args.repopath)

    if not os.path.exists(REPO_PATH):
        logger.error(f"Path to repo on disk not exists: '{REPO_PATH}'")
        exit(1)

    mode = "a" if args.append else "w"

    logger.debug(f"Disk files located in {REPO_PATH}")

    with open(args.logfile, mode) as f:
        print("--- Links checker log ---\n", file=f)  # create logfile

    logger.info("Check started!")

    for fname in sorted(os.listdir(args.path)):
        match = lpattern.match(fname)
        if not match:
            continue
        lecture_code = match.group(1)
        path = os.path.join(args.path, fname)
        check_lecture(path, lecture_code, args.logfile)

    logger.info("Check success!")
