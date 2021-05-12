import json
import os
import base64


def is_markdown(cell):
    return cell['cell_type'] == 'markdown'


def is_code(cell):
    return cell['cell_type'] == 'code'


def is_raw(cell):
    return cell['cell_type'] == 'raw'


def save_file(path, name, data):
    if len(data) == 1:
        for meme, base64str in data.items():
            with open(os.path.join(path, name), "wb") as f:
                f.write(base64.b64decode(base64str))
                print(f"Saved: {name}")
    else:
        print(f"Failed to save: {name}")


def save_attachments(path, attachments):
    for name, data in attachments.items():
        save_file(path, name, data)


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


def fix_markdown_cell(cell, i, total_i, path=""):
    global ctr
    if "attachments" in cell:
        print(f"Attachments was found in markdown cell {i}/{total_i}:")
        save_attachments(path, cell["attachments"])
        print("=" * 30)
        cell_text = "".join(cell["source"]).replace("\n\n", "\n")[:100]
        print(cell_text, "\n", "=" * 30)
        del cell["attachments"]
        ctr["attachments"] += 1

    if cell["metadata"] != dict():
        cell["metadata"] = dict()
        ctr["metadata"] += 1
    return cell


def process_one_lecture(pathname, overwrite=False):
    lecture_path = os.path.dirname(pathname)
    notebook_name = os.path.basename(pathname)
    if overwrite:
        clear_notebook_patch = pathname
    else:
        clear_notebook_patch = os.path.join(lecture_path, notebook_name.split(".")[0] + "_clear.ipynb")

    with open(pathname, "r") as inp:
        js = json.load(inp)

    new_js = dict()
    new_js["cells"] = list()
    total_i = len(js['cells'])

    for i, cell in enumerate(js['cells']):
        if is_markdown(cell):
            newcell = fix_markdown_cell(cell, i, total_i, lecture_path)
        elif is_code(cell):
            newcell = fix_code_cell(cell)
        elif is_raw(cell):
            newcell = cell
            print(f"Raw cell: {i}/{total_i}. Please fix it.")
        else:
            raise ValueError(f"Notebook broken. Unknown cell type: {cell['cell_type']}")

        new_js["cells"].append(newcell)

    old_global_meta = {key: value for key, value in js.items() if key != "cells"}
    new_js.update(old_global_meta)
    with open(clear_notebook_patch, "w", encoding='utf8') as out:
        json.dump(new_js, out, indent=1, ensure_ascii=False)
        out.write('\n')


class Counter(dict):
    def __init__(self):
        self["metadata"] = 0
        self["outputs"] = 0
        self["execution_count"] = 0
        self["attachments"] = 0

    def summary(self):
        if sum(list(self.values())) == 0:
            print("\tMy congratulations, notebook is perfect!")
        else:
            print(f"\tMetadata fixes: {self['metadata']}")
            print(f"\tOutputs fixes: {self['outputs']}")
            print(f"\tExecution fixes: {self['execution_count']}")
            print(f"\tAttachments fixes: {self['attachments']}")

    def reset(self):
        self.__init__()


MODE = "all_ipynb"
### If mode "one_ipynb", specify:
# lecture_pathname = "out//L13_GAN_cGAN//L13_GAN_cGAN.ipynb"

### If MODE == "all_ipynb", specify:
root = "out"

if __name__ == "__main__":
    ctr = Counter()
    if MODE == "one_ipynb":
        lecture_pathname = "out//L13_GAN_cGAN//L13_GAN_cGAN.ipynb"
        print(lecture_pathname)
        ctr.reset()
        process_one_lecture(lecture_pathname, overwrite=True)
        ctr.summary()
    if MODE == "all_ipynb":
        for path, subdirs, files in os.walk(root):
            for name in files:
                if name.endswith('.ipynb') and \
                        not ".ipynb_checkpoints" in path and \
                        not name.endswith('_clear.ipynb'):
                    lecture_pathname = os.path.join(path, name)

                    print(lecture_pathname)
                    ctr.reset()
                    process_one_lecture(lecture_pathname, overwrite=True)
                    ctr.summary()
