"""Module that implement functions set which allows to automatically set APIC tags to audio files.

Function auto implement auto tagging, other functions allow you to work with associations dict.
Structure of associations dict:
{"author": {"association name": path to img file}}
"""


from MP3.too_easy_mp3 import SimpleMP3, TagError
import pickle
import os.path
import os
from os import sep
import sys


def auto(file, associations, replace=True):
    """Set APIC tag to file using established associations which given by associations argument.
    This function need already established artist tag in file.

    OPTIONS
        replace: boolean
            If this option is False set APIC tag only if that tag isn't exist.
    """
    audio = SimpleMP3(file)
    artist = str(audio["artist"]).rstrip()
    if artist in associations:
        if replace:
            for key in associations[artist]:
                audio.set_img(associations[artist][key], key)
        else:
            for key in associations[artist]:
                try:
                    audio.get_img(f'..{sep}temp', img=key)
                except TagError:
                    audio.set_img(associations[artist][key], key)
    else:
        raise FormatError("No img associations for file " + file)


def load_associations(path):
    """Return dict of associations deserialized from path."""
    with open(path, "rb") as file:
        associations = pickle.load(file)
    return associations


def save_associations(assoc, path):
    """Save(serialize) assoc dict to path."""
    with open(path, "wb") as file:
        pickle.dump(assoc, file)


def add_association(assoc, author, img="", assoc_name=""):
    """Update assoc dict with new association.

    OPTIONS
        img: str
            Path to img file.
        assoc_name: str
            Name which be written after APIC: in tag.
    """
    if author not in assoc:
        assoc[author] = dict()
    assoc[author][assoc_name] = img


def associate(assoc, path, typ="", file=sys.stdout):
    """Update assoc with associated img to authors using file names, it will associate all files in directory
     so be careful.

     OPTIONS
        typ: str
            Name which be written after APIC: in tag, synonym to assoc_name.
        file: object
            File-like object (stream); defaults to the current sys.stdout.
     """
    out = file
    for el in os.listdir(path):
        el_path = path + sep + el
        if os.path.isfile(el_path):
            file = el.split(".")
            author = str()
            for i in range(len(file)-1):
                author += (file[i])
            img = el_path
            add_association(assoc, author, img, assoc_name=typ)
            print("association added" + " - " + author + " - " + img + " - " + typ, file=out)
        else:
            pass


def del_association(assoc, author, assoc_name=""):
    """Delete association from assoc.

    OPTIONS
        assoc_name: str
            Name which be written after APIC: in tag.
    """
    del(assoc[author][assoc_name])


def get_association(assoc, author):
    """Return association from assoc, as a list of lists([artist, 'APIC:' + assoc_name, path to img])."""
    res = list()
    if author in assoc:
        for key in assoc[author]:
            associations = str()
            associations += assoc[author][key]
            typ = "APIC:" + key
            res.append([author, typ, associations])
        return res
    else:
        return None


def get_associations(assoc):
    """Return all associations from assoc dict as a list of lists([artist, 'APIC:' + assoc_name, path to img])."""
    res = list()
    for author in assoc:
        for key in assoc[author]:
            associations = str()
            associations += assoc[author][key]
            typ = "APIC:" + key
            res.append([author, typ, associations])
    return res


def update_associations(assoc, path):
    """Update assoc dict with associations(must be pickle serialized dict) from path."""
    with open(path, "rb") as file:
        temp = pickle.load(file)
    assoc.update(temp)


def clear_associations():
    """Return clear dict of associations."""
    return dict()


class FormatError(Exception):
    """Error that is raised in the absence of association."""
    def __init__(self, value):
        self.value = value
