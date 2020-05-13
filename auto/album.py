"""Module that implement functions set which allows to automatically set album tags to audio files.

Function auto implement auto tagging, other functions allow you to work with associations dict.
Structure of associations dict:
{"author": {"association name": path to img file}}
"""


from MP3.too_easy_mp3 import SimpleMP3
import pickle
import os.path
import os
import sys


def auto(file, associations, replace=True):
    """Set album tag to file using established associations which given by associations argument.
    This function need already established artist nad title tag in file.

    OPTIONS
        replace: boolean
            If this option is False set album tag only if that tag isn't exist.
    """

    audio = SimpleMP3(file)
    artist = str(audio["artist"])
    title = str(audio["title"])
    if replace:
        if artist in associations:
            for el in associations[artist]:
                if title == el[0]:
                    audio["album"] = el[1]
        else:
            raise FormatError("No album associations for file " + file)
    else:
        if artist in associations:
            try:
                if not audio["album"]:
                    for el in associations[artist]:
                        if title == el[0]:
                            audio["album"] = el[1]
            except TypeError:
                pass
        else:
            raise FormatError("No album associations for file " + file)


def load_associations(path):
    """Return(Deserialize) dict of associations from path."""

    with open(path, "rb") as file:
        album_associations = pickle.load(file)
    return album_associations


def save_associations(assoc, path):
    """Save(Serialize) dict of associations to path."""

    with open(path, "wb") as file:
        pickle.dump(assoc, file)


def add_association(assoc, author, title="", album=""):
    """Update assoc dict with new association.

    OPTIONS
        title: str
            Used to set title of song which be associated with album.
        album: str
            Used to set album which be associated.
    """

    if author not in assoc:
        assoc[author] = list()
        assoc[author].append((title, album))
    else:
        for i in range(len(assoc[author])):
            if assoc[author][i][0] == title:
                assoc[author][i] = (title, album)
                return
        assoc[author].append((title, album))


def associate(assoc, path, album="", file=sys.stdout):
    """Update assoc dict with associated album to all mp3 in path(should be folder)

    OPTIONS
        album: str
            Used to set album which be associated.
        file: object
            File-like object (stream); defaults to the current sys.stdout.
     """
    out = file

    for el in os.listdir(path):
        el_path = path + "/" + el
        if os.path.isfile(el_path) and el_path.endswith(".mp3"):
            file = SimpleMP3(el_path)
            add_association(assoc, str(file["artist"]), title=str(file["title"]), album=album)
            print("association added" + " - " + str(file["artist"]) + " - " + str(file["title"]) + " - " + album,
                  file=out)
        else:
            pass


def del_association(assoc, author, title=""):
    """Delete association from assoc dict."""

    if author in assoc:
        for i in range(len(assoc[author])):
            if assoc[author][i][0] == title:
                del assoc[author][i]
                return


def get_associations(assoc):
    """Return all associations from assoc dict as a list of tuples((artist, song title, album)"""

    res = list()
    for author in assoc:
        try:
            for el in assoc[author]:
                res.append((author, el[0], el[1]))
        except IndexError:
            pass
    return res


def update_associations(assoc, path):
    """Update assoc dict with associations(must be pickle serialized dict) file from path"""

    with open(path, "rb") as file:
        temp = pickle.load(file)
    assoc.update(temp)


def clear_associations():
    """Return clear dict of associations"""

    return dict()


class FormatError(Exception):
    """Error that is raised in the absence of association."""
    def __init__(self, value):
        self.value = value
