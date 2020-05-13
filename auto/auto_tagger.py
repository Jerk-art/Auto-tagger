"""This module implement auto tagger class."""


import auto.name
import auto.img
import auto.album
import os.path
import sys


class AutoTagger:
    """Class used to link ban list and associations files with auto tagging functions, use auto tag functions
     and simplify editing associations dicts.
    """
    def __init__(self, ban_list, associations, album_associations, file=sys.stdout):
        """
        Construct a new 'AutoTagger' object.
        Load associations dicts and ban list from given path, when files not founded use empty dicts and list.

        :param file: file-like object to redirect output.
        :param ban_list: path to file which contain list of banned words/symbols.
        :param associations: path to file which contain dict of APIC associations.
        :param album_associations: path to file which contain dict of album associations.
        :return returns nothing.
        """

        self.ban_list = list()
        self.associations = auto.img.clear_associations()
        self.album_associations = auto.album.clear_associations()

        self.ban_list_path = ban_list
        self.associations_path = associations
        self.album_associations_path = album_associations
        self.file = file

        try:
            self.ban_list = auto.name.form_ban_list(self.ban_list_path)
            print("[Info]Ban list file loaded.", file=self.file)
        except FileNotFoundError:
            print("[Error]Ban list file not founded.", file=self.file)

        try:
            self.associations = auto.img.load_associations(self.associations_path)
            print("[Info]Img associations file loaded.", file=self.file)
        except FileNotFoundError:
            print("[Error]Img associations file not founded.", file=self.file)

        try:
            self.album_associations = auto.album.load_associations(self.album_associations_path)
            print("[Info]Album associations file loaded.", file=self.file)
        except FileNotFoundError:
            print("[Error]Album associations file not founded.", file=self.file)

    def auto_tag(self, path, replaces=None, parent=None):
        """
        Automatically set audio tags to file or files in directory.

        :param path: path to file or directory which should be tagged.
        :param replaces: dict of tkinter.VarInt, used to decide replace existing tags or not.
        Can contain 'Title', 'Artist', 'Image', 'Album' entries.
        :param parent: link to parent object which allows user to start tagging.
        Use parent stop attribute to check shouldn't be tagging interrupted.
        :return returns nothing
        """

        replace_title = True
        replace_artist = True
        replace_img = True
        replace_album = True

        if replaces:
            if replaces['Title'].get() == 0:
                replace_title = True
            else:
                replace_title = False
            if replaces['Artist'].get() == 0:
                replace_artist = True
            else:
                replace_artist = False
            if replaces['Image'].get() == 0:
                replace_img = True
            else:
                replace_img = False
            if replaces['Album'].get() == 0:
                replace_album = True
            else:
                replace_album = False

        if os.path.isfile(path):
            if path.endswith(".mp3"):
                name = os.path.split(path)[1]
                print("[Info]Adding tags to: " + name, file=self.file)
                auto.name.auto(path, self.ban_list, replace_artist=replace_artist, replace_title=replace_title)
                try:
                    auto.img.auto(path, self.associations, replace=replace_img)
                except auto.img.FormatError:
                    print("[Error]No img associations to file: " + name, file=self.file)
                except FileNotFoundError:
                    print("[Error]Failed to find img", file=self.file)
                try:
                    auto.album.auto(path, self.album_associations, replace=replace_album)
                except auto.album.FormatError:
                    print("[Error]No album associations to file: " + name, file=self.file)
            else:
                print("[ErrorCodeRed]Error: Not supported type", file=self.file)

        elif os.path.isdir(path):
            for el in os.listdir(path):
                if el.endswith(".mp3"):
                    print("[Info]Adding tags to: " + el, file=self.file)
                    auto.name.auto(os.path.normpath(path + "/" + el), self.ban_list,
                                   replace_artist=replace_artist, replace_title=replace_title)
                    try:
                        auto.img.auto(os.path.normpath(path + "/" + el), self.associations, replace=replace_img)
                    except auto.img.FormatError:
                        print("[Error]No img associations to file: " + el, file=self.file)
                    except FileNotFoundError:
                        print("[Error]Failed to find img", file=self.file)
                    try:
                        auto.album.auto(os.path.normpath(path + "/" + el),
                                        self.album_associations, replace=replace_album)
                    except auto.album.FormatError:
                        print("[Error]No album associations to file: " + el, file=self.file)
                    if parent:
                        if parent.stop:
                            return
        else:
            print("[ErrorCodeRed]Error: No such file or directory", file=self.file)

    def add_association(self, assoc_type, author, img="", assoc_name="", title="", album=""):
        """
        Update one of associations dict with new association.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :param author: string with artist name.
        :param img: string with path to img(used with assoc_type 'img').
        :param assoc_name: string with association name(used with assoc_type 'img').
        :param title: string with title(used with assoc_type 'album').
        :param album: string with album(used with assoc_type 'album').
        :return returns nothing.
        """
        if assoc_type == 'img':
            auto.img.add_association(self.associations, author, img=img, assoc_name=assoc_name)
        elif assoc_type == 'album':
            auto.album.add_association(self.album_associations, author, title=title, album=album)

    def associate(self, assoc_type, path, type_="", album="", file=sys.stdout):
        """
        Update one of associations dict with new associations established from given path.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :param path: path to associated directory.
        :param type_: string with name of img association(used with assoc_type 'img').
        :param album: string with album(used with assoc_type 'album').
        :param file: file-like object to redirect output.
        :return returns nothing.
        """
        if assoc_type == 'img':
            auto.img.associate(self.associations, path, typ=type_, file=file)
        elif assoc_type == 'album':
            auto.album.associate(self.album_associations, path, album=album, file=file)

    def del_association(self, assoc_type, author, assoc_name="", title=""):
        """
        Update delete one association from one of associations dict.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :param author: string with artist name.
        :param assoc_name: string with name of img association(used with assoc_type 'img').
        :param title: string with song title(used with assoc_type 'album').
        :return returns nothing.
        """
        if assoc_type == 'img':
            auto.img.del_association(self.associations, author, assoc_name=assoc_name)
        elif assoc_type == 'album':
            auto.album.del_association(self.album_associations, author, title=title)

    def get_associations(self, assoc_type):
        """
        Return associations from one of associations dict.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :return returns list of associations.
        """
        if assoc_type == 'img':
            return auto.img.get_associations(self.associations)
        elif assoc_type == 'album':
            return auto.album.get_associations(self.album_associations)

    def update_associations(self, assoc_type, path):
        """
        Update one of associations dict with pickle serialized dict from path.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :param path: string with path to file.
        :return returns nothing.
        """
        if assoc_type == 'img':
            auto.img.update_associations(self.associations, path)
        elif assoc_type == 'album':
            auto.album.update_associations(self.album_associations, path)

    def clear_associations(self, assoc_type):
        """
        Clear one of associations dict.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :return returns nothing.
        """
        if assoc_type == 'img':
            self.associations = auto.img.clear_associations()
        elif assoc_type == 'album':
            self.album_associations = auto.album.clear_associations()

    def save_associations(self, assoc_type):
        """
        Save changes in one of associations dict to his file.

        :param assoc_type: string with dict name(should be 'img' or 'album').
        :return returns nothing.
        """
        if assoc_type == 'img':
            auto.img.save_associations(self.associations, self.associations_path)
        elif assoc_type == 'album':
            auto.album.save_associations(self.album_associations, self.album_associations_path)
