import os
import re
import json
import base64
import argparse


def save_file(filepath, filename, data):
    if len(data) == 1:
        for meme, base64str in data.items():
            with open(os.path.join(filepath, filename), "wb") as f:
                f.write(base64.b64decode(base64str))
                print(f"\t[SAVED: {filename}]")
    else:
        print(f"\t[Failed to save: {filename}]")


def save_attachments(lect_path, attachments):
    for att_name, data in attachments.items():
        name_to_save = f"""img-{ctr["attachments"]}.{os.path.splitext(att_name)[1][1:].strip()}"""
        save_file(lect_path, name_to_save, data)


def check_and_fix_source(cell, lect_path, i, total_i):
    cell_text = "".join(cell["source"]).replace("\n", "")
    if "base64" in cell_text and args.warnings:
        print(f"\t[WARNING][Cell:{i + 1}/{total_i}]: Binary data found.")
        print("\t\t", cell_text[:150].rstrip())
        ctr["warnings"] += 1

    if "attachments" in cell:
        print(f"\t[WARNING][Cell:{i + 1}/{total_i}]: Markdown attachments found.")
        cell_text = "".join(cell["source"]).replace("\n", "")
        print("\t\t", cell_text[:100].rstrip())
        save_attachments(lect_path, cell["attachments"])
        del cell["attachments"]
        ctr["attachments"] += 1
    else:
        if re.match(r'^.*!\[.*\]\(.*\).*$', cell_text) is not None and args.warnings:
            print(f"\t[WARNING][Cell:{i + 1}/{total_i}]: Probably local link found.")
            print("\t\t", cell_text[:150].rstrip())
            ctr["warnings"] += 1
    return cell


def fix_code_cell(cell):
    if cell["execution_count"] is not None:
        cell["execution_count"] = None
        ctr["execution_count"] += 1
    if cell["metadata"] != dict():
        cell["metadata"] = dict()
        ctr["metadata"] += 1
    if cell["outputs"] != list():
        cell["outputs"] = list()
        ctr["outputs"] += 1
    return cell


def fix_markdown_cell(cell):
    if cell["metadata"] != dict():
        cell["metadata"] = dict()
        ctr["metadata"] += 1
    return cell


def process_one_lecture(pathname, overwrite=False):
    lecture_path = os.path.dirname(pathname)
    notebook_name = os.path.basename(pathname)

    with open(pathname, "r") as inp:
        js = json.load(inp)

    new_js = dict()
    new_js["cells"] = list()
    total_i = len(js['cells'])

    for i, cell in enumerate(js['cells']):
        cell = check_and_fix_source(cell, lecture_path, i, total_i)
        if cell['cell_type'] == 'markdown':
            new_cell = fix_markdown_cell(cell)
        elif cell['cell_type'] == 'code':
            new_cell = fix_code_cell(cell)
        elif cell['cell_type'] == 'raw':
            new_cell = cell
            print(f"Raw cell: {i + 1}/{total_i}. Please fix it.")
        else:
            raise ValueError(f"Notebook broken. Unknown cell type: {cell['cell_type']}")

        new_js["cells"].append(new_cell)

    if ctr.is_changed():
        save_patch = pathname
        if not overwrite:
            backup_patch = os.path.join(lecture_path, notebook_name.split(".")[-2] + "_backup.ipynb")
            os.replace(pathname, backup_patch)

        old_global_meta = {key: value for key, value in js.items() if key != "cells"}
        new_js.update(old_global_meta)
        with open(save_patch, "w", encoding='utf8') as out:
            json.dump(new_js, out, indent=1, ensure_ascii=False)
            out.write('\n')


class Counter(dict):
    def __init__(self):
        self["metadata"] = 0
        self["outputs"] = 0
        self["execution_count"] = 0
        self["attachments"] = 0
        self["warnings"] = 0
        self["n_image"] = 0

    def summary(self):
        if sum(list(self.values())) == 0:
            print("\tMy congratulations, notebook is perfect!")
        else:
            if self['warnings'] != 0: print(f"\tWarings: {self['warnings']}")
            if self['metadata'] != 0: print(f"\tMetadata fixes: {self['metadata']}")
            if self['outputs'] != 0: print(f"\tOutputs fixes: {self['outputs']}")
            if self['execution_count'] != 0: print(f"\tExecution counts fixes: {self['execution_count']}")
            if self['attachments'] != 0: print(f"\tAttachments fixes: {self['attachments']}")

    def reset(self):
        self.__init__()

    def is_changed(self):
        if sum(list(self.values())) - self['warnings'] == 0:
            return False
        else:
            return True


def main():
    if args.filepath is not None:
        lecture_pathname = args.filepath
        print(lecture_pathname)
        ctr.reset()
        process_one_lecture(lecture_pathname, overwrite=args.overwrite)
        ctr.summary()
    else:
        for path, subdirs, files in os.walk(args.root):
            for name in files:
                if name.endswith('.ipynb') and \
                        ".ipynb_checkpoints" not in path and \
                        not name.endswith('_backup.ipynb'):
                    lecture_pathname = os.path.join(path, name)

                    print(lecture_pathname)
                    ctr.reset()
                    process_one_lecture(lecture_pathname, overwrite=args.overwrite)
                    ctr.summary()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for cleaning notebooks.')
    parser.add_argument('--disable-backup', dest='overwrite', action='store_true',
                        help="If provided, overwrites target notebook, else create a ipynb backup.")
    parser.add_argument('--disable-warnings', dest='warnings', action='store_false',
                        help="Script disable warnings like 'Probably local link found.'")
    parser.add_argument('--filepath', default=None,
                        help='Notebook filepath, if not provided, script processed all files in root.')
    parser.add_argument('--root', default="out",
                        help="""(default:"out") Processed all file in root folder and all subfolders.""")
    parser.set_defaults(overwrite=False)
    parser.set_defaults(warnings=True)

    args = parser.parse_args()
    ctr = Counter()
    main()
