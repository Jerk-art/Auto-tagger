"""Module that implement functions set which allows to automatically set artist and title tags to audio files."""


from MP3.too_easy_mp3 import SimpleMP3
import os


def auto(file, ban_list, replace_artist=True, replace_title=True):
    """If file doesn't have any tags add them.  Generate audio tags using filename splitted by '-'.
    First element of received list interpreted as artist, others as a song name.  ban_list is a path to file that
    contain phrases and symbols which be later replaced by ' '.

    OPTIONS
        replace_artist: boolean
            If this option is False set artist tag only if that tag isn't exist.

        replace_title: boolean
            If this option is False set title tag only if artist tag isn't exist.
    """
    audio = SimpleMP3(file)
    name = os.path.split(file)[1]
    name = name.replace(".mp3", "")

    for el in ban_list:
        name = name.replace(el, " ").rstrip()

    tags = name.split("-")
    title = str()
    artist = tags[0].title()
    artist = artist.strip()

    if replace_artist:
        audio["artist"] = artist
    else:
        try:
            if not audio["artist"]:
                audio["artist"] = artist
        except AttributeError:
            pass

    for i in range(1, len(tags)):
        title = title + " " + str(tags[i])
    title = title.title().strip()

    if replace_title:
        audio["title"] = title
    else:
        try:
            if not audio["title"]:
                audio["title"] = artist
        except AttributeError:
            pass


def form_ban_list(path):
    """Form list of baned words using file from path."""
    ban_list = list()
    with open(path, "r", encoding="utf8") as file:
        for line in file:
            ban_list.append(line.replace("\n", ""))
    return ban_list


def ban_item(ban_list, item):
    """Add item to given list."""
    ban_list.append(item)


def pardon_item(ban_list, item):
    """Remove item from list."""
    ban_list.remove(item)


def save_list(ban_list, path):
    """Save list to file from path."""
    with open(path, "w", encoding="utf8") as file:
        for el in ban_list:
            el += "\n"
            file.write(el)
