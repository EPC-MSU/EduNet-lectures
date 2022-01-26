import os
import re
import base64
import argparse

import nbformat


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


def check_and_fix_source(cell, lect_path, count_cells, i):
    cell_text = "".join(cell["source"]).replace("\n", "")
    if "attachments" in cell:
        print(f"\t[WARNING][Cell:{i + 1}/{count_cells}]: Markdown attachments found.")
        cell_text = "".join(cell["source"]).replace("\n", "")
        print("\t\t", cell_text[:100].rstrip())
        save_attachments(lect_path, cell["attachments"])
        del cell["attachments"]
        ctr["attachments"] += 1
    if ";base64," in cell_text and args.warnings:
        print(f"\t[WARNING][Cell:{i + 1}/{count_cells}]: Binary data found.")
        print("\t\t", cell_text[:150].rstrip())
        ctr["warnings"] += 1
    else:
        if re.match(r'^.*!\[.*\]\(.*\).*$', cell_text) is not None and args.warnings:
            print(f"\t[WARNING][Cell:{i + 1}/{count_cells}]: Probably local link found.")
            print("\t\t", cell_text[:150].rstrip())
            ctr["warnings"] += 1
    return cell


def count_fixes(cell):
    if 'execution_count' in cell:
        if cell["execution_count"] is not None:
            if cell["execution_count"] != 0:
                ctr["execution_count"] += 1
    if cell["metadata"] != nbformat.NotebookNode():
        ctr["metadata"] += 1
    if 'outputs' in cell:
        if cell["outputs"] != list():
            ctr["outputs"] += 1
    if cell['cell_type'] == 'raw':
        print(f"\t[WARNING][Cell:]: Raw cell. Please fix cell type.")  # {i + 1}/{total_i}


def fix_cell(cell, lecture_path, count_cells, i):
    cell = check_and_fix_source(cell, lecture_path, count_cells, i)
    d_to_save = {'cell_type': cell['cell_type'],
                 'metadata': nbformat.NotebookNode(),
                 'source': cell['source']}
    if cell['cell_type'] == 'code':
        d_to_save['execution_count'] = 0
        d_to_save['outputs'] = []
    return nbformat.from_dict(d_to_save)


def fix_cells(cells, lecture_path):
    new_cells = []
    for i, cell in enumerate(cells):  # 167
        count_fixes(cell)
        new_cell = fix_cell(cell, lecture_path, len(cells), i)
        new_cells.append(new_cell)
    return new_cells


def process_one_lecture(pathname, backup):
    lecture_path = os.path.dirname(pathname)
    notebook_name = os.path.basename(pathname)
    if backup:
        backup_patch = os.path.join(lecture_path, notebook_name.split(".")[-2] + "_backup.ipynb")
        os.replace(pathname, backup_patch)
        lect_unchanged = nbformat.read(backup_patch, as_version=nbformat.NO_CONVERT)
    else:
        lect_unchanged = nbformat.read(pathname, as_version=nbformat.NO_CONVERT)

    new_cells = fix_cells(lect_unchanged["cells"], lecture_path)

    new_nb = lect_unchanged
    new_nb['cells'] = new_cells
    new_nb['metadata'] = nbformat.NotebookNode()
    nbformat.validate(new_nb)
    nbformat.write(new_nb, pathname, version=nbformat.NO_CONVERT)


class Counter(dict):
    def __init__(self):
        super().__init__()
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
    nothing_to_fix = True
    if args.filepath is not None:
        lecture_pathname = args.filepath
        print(lecture_pathname)
        ctr.reset()
        process_one_lecture(lecture_pathname, backup=args.backup)
        ctr.summary()
        nothing_to_fix = False

    else:
        for path, subdirs, files in os.walk(args.root if args.root is not None else "."):
            for name in files:
                if name.endswith('.ipynb') and \
                        ".ipynb_checkpoints" not in path and \
                        not name.endswith('_backup.ipynb'):
                    lecture_pathname = os.path.join(path, name)
                    print(lecture_pathname)
                    ctr.reset()
                    process_one_lecture(lecture_pathname, backup=args.backup)
                    ctr.summary()
                    nothing_to_fix = False
            if args.root is None:
                break
    if nothing_to_fix is True:
        print("Nothing to fix (No one lectures in path)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for cleaning notebooks.')
    parser.add_argument('--backup', dest='backup', action='store_true',
                        help="If provided, create a ipynb backup.")
    parser.add_argument('--disable-warnings', dest='warnings', action='store_false',
                        help="Script disable warnings like 'Probably local link found.'")
    parser.add_argument('--filepath', default=None,
                        help='Notebook filepath, if not provided, script processed all files in root, if root '
                             'not provided, processed all file in current directory.')
    parser.add_argument('--root', default=None,
                        help="""(default:"None") Processed all file in root folder and all subfolders.""")
    parser.set_defaults(backup=False)
    parser.set_defaults(warnings=True)

    args = parser.parse_args()
    ctr = Counter()
    main()
