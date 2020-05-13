"""Module implement SimpleMP3 class to simplify use of mutagen ID3 class.
supported_tags is a dict with ID3 tags as keys and their SimpleMP3 synonyms as values.
"""


from mutagen.id3 import ID3, TIT2, TALB, TPE1, APIC, TRCK, TDRC, ID3NoHeaderError
import MP3.hash_func
import filetype
import os.path


supported_tags = {"TIT2": "title", "TPE1": "artist", "TALB": "album", "TDRC": "year",
                               "TRCK": "number", "APIC": "icon"}


class SimpleMP3:
    """
    Provide an easy access to tags and hash function
    """
    def __init__(self, path):
        """
        Construct a new 'SimpleMP3' object.
        Load associations dicts and ban list from given path, when files not founded use empty dicts and list.

        :param path: path to file.
        :return returns nothing.
        """
        self.path = path
        if path.endswith(".mp3"):
            try:
                self.audio = ID3(path)
            except ID3NoHeaderError:
                self.audio = ID3()
        else:
            raise FormatError("Not supported extension")

    def __setitem__(self, k, val):
        if k == "title":
            if val is None:
                val = ""
            self.audio["TIT2"] = TIT2(encoding=3, text=val)
            self.audio.save(self.path)
        elif k == "artist":
            if val is None:
                val = ""
            self.audio["TPE1"] = TPE1(encoding=3, text=val)
            self.audio.save(self.path)
        elif k == "album":
            if val is None:
                val = ""
            self.audio["TALB"] = TALB(encoding=3, text=val)
            self.audio.save(self.path)
        elif k == "year":
            if val is None:
                val = ""
            self.audio["TDRC"] = TDRC(encoding=3, text=val)
            self.audio.save(self.path)
        elif k == "number":
            if val is None:
                val = ""
            self.audio["TRCK"] = TRCK(encoding=3, text=val)
            self.audio.save(self.path)
        else:
            raise TagError("Tag {} not supported".format(k))

    def __getitem__(self, k):
        try:
            if k == "title":
                return self.audio["TIT2"]
            elif k == "artist":
                return self.audio["TPE1"]
            elif k == "album":
                return self.audio["TALB"]
            elif k == "year":
                return self.audio["TDRC"]
            elif k == "number":
                return self.audio["TRCK"]
            else:
                raise TagError("Tag {} not supported".format(k))
        except KeyError:
            return None

    def __delitem__(self, k):
        element = self[k]
        if element is None:
            return
        self[k] = None

    def __iter__(self):
        yield "title"
        yield "artist"
        yield "album"
        yield "year"
        yield "number"

    def get_hash(self):
        """Return sha256 of file."""
        return MP3.hash_func.file_sha256(self.path)

    def set_img(self, path_to_img, img="Front cover"):
        """Set APIC to file.

        :param path_to_img: path to img file.
        :param img: img name(APIC:img).
        :return returns nothing.
        """
        image_data = bytes()
        with open(path_to_img, "rb") as file:
            for bit in file:
                image_data += bit
        self.audio.add(APIC(3, 'image/jpeg', 3, img, image_data))
        self.audio.save(self.path)

    def get_img_ext(self, img=None):
        """Get APIC image extension.

        :param img: img name(APIC:img)
        :return returns nothing.
        """
        image_data = None
        if not img:
            tags = self.get_tag_list()
            for el in tags:
                if isinstance(el, list):
                    try:
                        if el[0].startswith('APIC'):
                            image_data = self.audio[el[0]].data
                            break
                    except IndexError:
                        pass
        else:
            temp = list()
            for k in self.audio:
                temp.append(k)
            if "APIC:" + img in temp:
                image_data = self.audio["APIC:" + img].data
            else:
                raise TagError("No such tag APIC:" + img)
        return filetype.guess(image_data).extension

    def get_img(self, aimg, img=None):
        tag_founded = False
        if not img:
            tags = self.get_tag_list()
            for el in tags:
                if isinstance(el, list):
                    try:
                        if el[0].startswith('APIC'):
                            imagedata = self.audio[el[0]].data
                            tag_founded = True
                            break
                    except IndexError:
                        pass
        else:
            temp = list()
            for k in self.audio:
                temp.append(k)
            if "APIC:" + img in temp:
                imagedata = self.audio["APIC:" + img].data
                tag_founded = True
            else:
                raise TagError("No such tag APIC:" + img)

        if not tag_founded:
            raise TagError("No such tag APIC:")

        kind = filetype.guess(imagedata)
        path = aimg + "." + kind.extension
        file = open(path, "wb")
        file.write(imagedata)
        file.close()
        return path

    def del_img(self, al=False, img=""):
        if not al:
            self.audio.delall('APIC:' + img)
            self.audio.save(self.path)
        else:
            self.audio.delall("APIC")
            self.audio.save(self.path)

    def get_tag_list(self):
        res = list()
        apic = list()
        comm = list()
        for tag in self.audio:
            if tag.startswith("APIC"):
                apic.append(tag)
            if tag.startswith("COMM"):
                comm.append(tag)
            elif tag in supported_tags:
                res.append(tag)
        res.append(apic)
        res.append(comm)
        return res

    def get_size(self):
        return os.path.getsize(self.path)


class TagError(Exception):
    def __init__(self, value):
        self.value = value


class FormatError(Exception):
    def __init__(self, value):
        self.value = value
