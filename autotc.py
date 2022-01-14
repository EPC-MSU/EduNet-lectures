import json
import os
import re
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmt = logging.Formatter("[%(levelname)s] [%(asctime)s] %(name)s: %(message)s")
ch.setFormatter(fmt)
logger.addHandler(ch)


base_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(base_dir, "out")
cur_file = os.path.join(out_dir, "Curriculum.md")

lpattern = re.compile(r"L\d+(_\w*)?\.ipynb")  # filename pattern
tpattern = re.compile(r".*<.*>(.*)<\/.*>.*")  # title pattern
hpattern = re.compile(r"#{1,2}\s*([^#\n<>]+)")  # header pattern


def analyze_lecture(fname):
    path = os.path.join(out_dir, fname)
    with open(path, encoding="utf-8") as f:
        lecture = json.load(f)
    cells = lecture.get("cells")
    if not cells:
        logger.warning(f"File '{fname}' incorrect")
        return
    title_src = "".join(cells[0]["source"])
    title = tpattern.match(title_src)
    if not title:
        logger.warning(f"Lecture's title not found, using name '{fname}'")
        title = fname
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


def main():
    lectures = {}
    for fname in sorted(os.listdir(out_dir)):
        if not lpattern.fullmatch(fname):
            continue
        title, headers = analyze_lecture(fname)
        lectures[title] = headers

    logger.info(f"Total analyzed: {len(lectures)}")
    
    if os.path.isfile(cur_file):
        logger.info("Curriculum.md exists, writing in Curriculum_Temp.md")
        path = os.path.join(out_dir, "Curriculum_Temp.md")
    else:
        path = cur_file
    
    generate_md(lectures, path)


if __name__ == "__main__":
    main()

