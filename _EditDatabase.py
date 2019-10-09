#!/usr/bin/env python3
import driver
import util

CLASSES = [driver.model.Account, driver.model.Location, driver.model.Person]


def func_append():
    print("\nWhat to add:")
    aClass, index = util.Serialization.pick_from_list(CLASSES)
    filepath = getattr(aClass, "FILE", None)
    assert(filepath is not None)

    init_code = aClass.__init__.__code__
    init_vars = init_code.co_varnames[1:init_code.co_argcount]
    args = {}

    print("\nAdd " + aClass.__name__)
    for var in init_vars:
        print(var + ": ", end='')
        args[var] = input()
    new = aClass(**args)
    print(new)
    util.Serialization.append(item=new, path=filepath)
    print("\n\nFILE:")
    print('\n'.join([str(x) for x in util.Serialization.load(filepath)]))


def func_remove():
    print("\nWhat to remove:")
    aClass, index = util.Serialization.pick_from_list(CLASSES)
    filepath = getattr(aClass, "FILE", None)
    assert(filepath is not None)
    print("\nRemove which " + aClass.__name__)

    list = util.Serialization.load(filepath)
    instance, index = util.Serialization.pick_from_list(list)
    list.remove(instance)
    util.Serialization.save(path=filepath, list=list)
    print("\nRemoved " + str(instance))
    print("\n\nFILE:")
    print('\n'.join([str(x) for x in util.Serialization.load(filepath)]))


def func_list():
    print("\nList what:")
    aClass, index = util.Serialization.pick_from_list(CLASSES)
    filepath = getattr(aClass, "FILE", None)
    assert(filepath is not None)
    print("\n" + aClass.__name__ + " on file:")
    list, all = util.Serialization.load(filepath, filter_class=aClass)
    util.Serialization.print_list(list)


def main():
    run = True
    while run:
        func_map = {"Add": func_append,
                    "Remove": func_remove,
                    "List": func_list}

        value, index = util.Serialization.pick_from_list(
            list(func_map.keys()), sort=False)
        func_map[value]()
        if not util.Utils.query_yes_no("\nAgain?", "no"):
            run = False


#   ///////////////////////////
#  ////////// MAIN ///////////
# ///////////////////////////
if __name__ == "__main__":
    util.Utils.clear_screen("_EditModelInstrances.py")
    main()
    print("\nDone\n")
