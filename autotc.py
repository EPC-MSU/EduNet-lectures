import json
import os
import re
import logging
import argparse


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmt = logging.Formatter("[%(levelname)s] [%(asctime)s] %(name)s: %(message)s")
ch.setFormatter(fmt)
logger.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument("--dir", help="Directory with notebooks to process", default="out")
parser.add_argument("--output", help="Output filename", default="temp_Curriculum.md")

lpattern = re.compile(r"L\d+(_\w*)?\.ipynb")  # filename pattern
tpattern = re.compile(r".*<.*>(.*)<\/.*>.*")  # title pattern
hpattern = re.compile(r"#{1,2}\s*([^#\n<>]+)")  # header pattern


def analyze_lecture(path):
    with open(path, encoding="utf-8") as f:
        lecture = json.load(f)
    cells = lecture.get("cells")
    if not cells:
        logger.warning(f"File '{fname}' incorrect")
        return
    title_src = "".join(cells[0]["source"])
    title = tpattern.match(title_src)
    if not title:
        title = os.path.basename(path)
        logger.warning(f"Lecture's title not found, using name '{title}'")
    else:
        title = title.group(1).strip()
    headers = []
    for v in cells[1:]:
        if v["cell_type"] != "markdown":
            continue
        for source in v["source"]:
            header = hpattern.match(source.strip())
            if not header:
                continue
            headers.append(header.group(1))
    return title, headers


def generate_md(lectures, path):
    f = open(path, "w", encoding="utf-8")
    print("Программа курса\n", file=f)
    i = 1
    for title, headers in lectures.items():
        print(f"## Лекция {i} “{title}”\n", file=f)
        print(". ".join(headers) + "\n", file=f)
        i += 1
    f.close()
    logger.info(f"File created: {path}")


def main():
    args = parser.parse_args()
    out_dir = os.path.abspath(args.dir)
    lectures = {}
    for fname in sorted(os.listdir(out_dir)):
        if not lpattern.fullmatch(fname):
            continue
        title, headers = analyze_lecture(os.path.join(out_dir, fname))
        lectures[title] = headers
    logger.info(f"Total analyzed: {len(lectures)}")
    generate_md(lectures, os.path.join(out_dir, args.output))


if __name__ == "__main__":
    main()

