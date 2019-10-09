import jsonpickle
import os
import shutil
from datetime import datetime
import threading

#
# => Write
#

lock = threading.RLock()


def save(list, path, backup=True):
    with lock:
        if backup is True:
            _backup_data(path)
        with open(path, "w+") as file:
            file.writelines([jsonpickle.encode(item) + "\n" for item in list])


def _backup_data(path, subfolder="backups"):
    try:
        backup_file = os.path.dirname(
            path) + "/" + subfolder + "/" + os.path.basename(path) + "-" + str(datetime.now())
        shutil.copyfile(path, backup_file)
    except FileNotFoundError:
        pass

# returns: (value, index)


def append(item, path):
    with lock:
        _backup_data(path)
        with open(path, "a+") as file:
            file.write(jsonpickle.encode(item) + "\n")
#
# => Read .jl
#

# passing filter class turns return value into tuple


def load(path, filter_class=None):
    all = []

    with lock:
        try:
            with open(path) as file:
                all = [jsonpickle.decode(line) for line in file]
        except IOError:
            pass

    if filter_class is None:
        return all
    else:
        return [x for x in all if isinstance(x, filter_class)], all

#
#
# Printing
#
#


# returns: item, index
def pick(path, default_value=None, sort=True):
    assert(default_value is None or type(default_value) is int)
    items = load(path)
    return pick_from_list(items, default_value, sort=sort)


# returns: item, index
def pick_from_list(picklist, default_value=None, sort=True):
    original_list = picklist.copy()
    if sort:
        picklist.sort(key=str)

    print_list(picklist, sort)
    default_string = "" if default_value is None else "[{}] ".format(
        default_value)
    query_string = "Choose an option: " + default_string

    str_input = input(query_string)
    if len(str_input) == 0 and default_value is not None:
        str_input = str(default_value)
    index = int(str_input)
    item = picklist[index]
    index = original_list.index(item)
    print("Picked {}".format(item))
    return item, index


# returns: (nonnull) [item], (nonnull) [index]
def picks_from_list(picklist):
    print_list(picklist, sort=False)
    choices = input("Choose options [ex: '1,3,..']: ")

    # return with no results
    if len(choices) == 0:
        return [], []

    indexes = [int(i) for i in sorted(choices.split(","))]
    items = [picklist[i] for i in indexes]

    print("Picked: \n{}".format('\n'.join(items)))
    return items, indexes


def print_list(objlist, sort=True, add_space_every_ten_lines=False):
    options = [" {:3}. {}".format(i, item)
               for (i, item) in enumerate(objlist)]
    if sort:
        # 6 is used here because it is the length of "  ##. "
        options.sort(key=lambda x: x[6:])

    if add_space_every_ten_lines:
        positions = range(0, len(options), 10)
        ordering = reversed(list(positions))
        for index in ordering:
            options.insert(index, "")

    options_string = '\n'.join(options)
    print(options_string)
