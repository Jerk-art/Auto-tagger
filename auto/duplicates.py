import os
import os.path
from MP3.hash_func import file_sha256 as hash


def find_duplicates(path, mutex=None):
    if mutex is None:
        if os.path.isdir(path):
            pass
        else:
            raise SearchError("No such directory")

        sizes = list()
        for el in os.listdir(path):
            if el.endswith(".mp3"):
                print("Checking: " + el)
                el = os.path.normpath(path + "/" + el)
                sizes.append([el, os.path.getsize(el)])
            else:
                pass

        print("Checking complete")

        dsizes = dict()

        for el in sizes:
            for el2 in sizes:
                if el == el2:
                    pass
                elif el[1] == el2[1]:
                    dsizes[el[0]] = el[1]
                    dsizes[el2[0]] = el2[1]

        for key in dsizes:
            print("Hashing file: " + key)
            dsizes[key] = hash(key)

        res = list()

        for key in dsizes:
            for key2 in dsizes:
                if dsizes[key] == dsizes[key2]:
                    item = [[key], dsizes[key]]
                    if item not in res:
                        res.append(item)
        return res
    else:
        if os.path.isdir(path):
            pass
        else:
            mutex.acquire()
            print("No such directory")
            mutex.release()
            return

        sizes = list()
        for el in os.listdir(path):
            if el.endswith(".mp3"):
                mutex.acquire()
                print("Checking: " + el)
                mutex.release()
                el = os.path.normpath(path + "/" + el)
                sizes.append([el, os.path.getsize(el)])
            else:
                pass

        mutex.acquire()
        print("Checking complete")
        mutex.release()

        dsizes = dict()

        for el in sizes:
            for el2 in sizes:
                if el == el2:
                    pass
                elif el[1] == el2[1]:
                    dsizes[el[0]] = el[1]
                    dsizes[el2[0]] = el2[1]

        for key in dsizes:
            mutex.acquire()
            print("Hashing file: " + key)
            mutex.release()
            dsizes[key] = hash(key)

        res = list()

        for key in dsizes:
            for key2 in dsizes:
                if dsizes[key] == dsizes[key2]:
                    item = [[key], dsizes[key]]
                    if item not in res:
                        res.append(item)
        for el in res:
            mutex.acquire()
            print(el)
            mutex.release()


class SearchError(Exception):
    def __init__(self, value):
        self.value = value
