"""This module provides classes to mTool GUI based on tkinter and ttk widgets."""


from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.messagebox import showerror
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
from PIL.ImageTk import PhotoImage
from PIL import Image
from MP3.too_easy_mp3 import SimpleMP3, supported_tags, TagError
from os import remove, listdir, popen
from threading import Thread
from os.path import sep
from shutil import copyfile
import auto.auto_tagger as tagger


class LoadingFrame(ttk.Frame):
    """Widget that provides a frame which can be used to chose folders and load other part of GUI by overriding
    command_open method.
    """
    def __init__(self, parent=None, style='LoadingWindow', **options):
        """
        Construct a new 'LoadingFrame' object.

        :attribute style: string with style name.
        :attribute folder: path to open folder.
        :attribute label: label object with animated part of widget.
        :return returns nothing.
        """
        ttk.Frame.__init__(self, parent, style=style + '.TFrame', **options)
        self.style = style
        self.folder = None
        self.label = None
        self.make_widget()

    def make_widget(self):
        """
        This method construct widgets inside LoadingFrame object.

        :return returns nothing.
        """

        self.label = ttk.Label(self, style=self.style + '.TLabel', text='Waiting for folder', font='36', anchor=CENTER)
        self.label.pack(side=TOP, expand=YES, fill=BOTH, pady=30)

        buttons_holder = ttk.Frame(self, style=self.style + '.TFrame')
        buttons_holder.pack(side=TOP, expand=YES, padx=40)
        ttk.Button(buttons_holder, text='Choose folder', command=self.command_chose_folder,
                   width=20, style=self.style + '.TButton').pack(side=LEFT, padx=2)
        ttk.Button(buttons_holder, text='Open', command=self.command_open, style=self.style + '.TButton',
                   width=20).pack(side=LEFT, pady=8)

        ttk.Frame(self, style=self.style + '.TFrame', height=25).pack(side=TOP, fill=X, expand=YES)

    def command_chose_folder(self):
        """
        This method called when pressed 'Choose folder' button. Call askdirectory and write result to folder attribute.

        :return returns nothing.
        """
        self.folder = askdirectory(title='Open..')

    def command_open(self):
        """
        This method called when pressed 'open' button. Basically call animate_it, need to be overriden.

        :return returns nothing.
        """
        if self.folder:
            text = 'Loading'
            self.animate_it(text)

    def animate_it(self, text):
        """
        Make simple animation.

        :return returns nothing.
        """
        self.label.config(text=text)
        text = text + '.'
        if len(text) == 11:
            text = 'Loading'
        self.after(500, self.animate_it, text)


class File(Frame):
    """Widget that makes audio file representation"""
    def __init__(self, parent=None, file_path='', style='File', **options):
        """
        Construct a new 'File' object using mp3 file.

        :param style: string with style name.
        :param file_path: path to file.
        :return returns nothing.
        """
        Frame.__init__(self, parent, options)
        self.file = SimpleMP3(file_path)
        self.style = style
        self.cur_style = self.style
        self.active = False
        self.checkbutton = None
        self.background = None

        self.var = IntVar()

        self.canvas = Canvas(self, bg=ttk.Style().lookup(self.cur_style + '.Canvas', 'bg'),
                             height=46, highlightthickness=0)
        self.canvas.pack(side=RIGHT, expand=YES, fill=X)
        self.draw_content()

    def draw_content(self):
        """
        Decide how to make 'File' object and call appropriate method.

        :return returns nothing.
        """
        if self.file['title'] and self.file['artist']:
            self.draw_by_tags()
        else:
            self.draw_by_filename()

    def draw_by_tags(self):
        """
        Create widgets inside 'File' object using file tags.

        :return returns nothing.
        """
        self.checkbutton = ttk.Checkbutton(self, variable=self.var, style=self.cur_style + '.TCheckbutton',
                                           takefocus=False)
        self.canvas.create_window(2, 19, window=self.checkbutton, anchor=W, tag='file')
        self.canvas.create_text(31, 13, text=self.file['title'], tag='text', anchor=W)
        self.canvas.create_text(31, 34, text=self.file['artist'], tag='text', anchor=W)

    def draw_by_filename(self):
        """
        Create widgets inside 'File' object using file name.

        :return returns nothing.
        """
        self.checkbutton = ttk.Checkbutton(self, variable=self.var, style=self.cur_style + '.TCheckbutton',
                                           takefocus=False)
        self.canvas.create_window(2, 19, window=self.checkbutton, anchor=W, tag='file')
        self.canvas.create_text(31, 22, text=self.file.path.split(sep)[-1], tag='text', fill='#4f4f4f', anchor=W)

    def refresh(self, style=None):
        """
        Reload audio file.

        :param style: used to chose style.
        :return returns nothing.
        """
        if style:
            self.cur_style = style
            self.background = ttk.Style().lookup(self.cur_style + '.Canvas', 'bg')
        self.canvas.config(bg=self.background)
        self.file = SimpleMP3(self.file.path)
        self.canvas.delete('text')
        self.draw_content()

    def refresh_state(self):
        """
        Change style and active attribute.

        :return returns nothing.
        """
        if self.active:
            self.refresh(style=self.style)
            self.active = False
        else:
            self.refresh(self.style + '.Active')
            self.background = ttk.Style().lookup(self.cur_style + '.Canvas', 'bg')
            self.active = True


class FileSection(Frame):
    """Widget that provides section of 'File' widgets"""
    def __init__(self, parent=None, dir_='', styles=None, **options):
        """
        Construct a new 'FileSection' object using path to directory with mp3 files.

        :param dir_: string with path to directory.
        :param styles: list with names of styles that be used to create 'File' widgets one by one.
        :attribute first_file: path to first audio file in directory.
        :return returns nothing.
        """
        Frame.__init__(self, parent, **options)

        vertical_delimiter = Frame(self, width=1, bg='grey')
        vertical_delimiter.pack(side=LEFT, fill=Y)

        cur_dir_holder = Frame(self, bg='grey')
        cur_dir_holder.pack(side=TOP, fill=BOTH)

        vertical_delimiter = Frame(cur_dir_holder, width=1, bg='grey')
        vertical_delimiter.pack(side=RIGHT, fill=Y)

        self.prev_widget = None
        self.first_file = None

        try:
            text = dir_.split(sep)[-2] + sep + dir_.split(sep)[-1]
        except IndexError:
            try:
                text = dir_.split('/')[-2] + '/' + dir_.split('/')[-1]
            except IndexError:
                text = dir_

        self.cur_dir = Label(cur_dir_holder, text=text,
                             font='Verdana 13', bg='white')
        self.cur_dir.pack(side=TOP, fill=BOTH, pady=1)
        self.styles = styles
        self.files = dict()

        self.canvas = Canvas(self, bg=self['bg'], highlightthickness=0, width=self['width'])
        self.sbar = Scrollbar(self)

        self.sbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.sbar.set, yscrollincrement=10)
        self.sbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=RIGHT, expand=YES, fill=BOTH)

        self.load_files(dir_)

    def load_files(self, dir_):
        """
        Load files and create 'File' widgets.

        :param dir_: string with path to directory.
        :return returns nothing.
        """
        scroll_region_max_y = 0
        self.first_file = None

        for file in listdir(dir_):
            if not file.endswith('.mp3'):
                continue

            if not self.first_file:
                self.first_file = dir_ + sep + file

            style = self.styles[0]
            self.styles = self.styles[1:]
            self.styles.append(style)

            path = dir_ + sep + file
            widget = File(self.canvas, path, style=style)
            self.canvas.create_window(0, scroll_region_max_y, window=widget, anchor=NW, tag='file')
            self.files[file] = widget
            widget.canvas.bind('<1>', (lambda event, widget_=widget: self.on_click(widget_)))
            widget.canvas.bind('<Double-1>', (lambda event, widget_=widget: self.on_double(widget_)))
            self.bind_all('<Up>', (lambda event: print(event.widget)))

            scroll_region_max_y += int(widget.canvas['height'])

            widget.canvas.bind('<MouseWheel>', (lambda event:
                                                self.canvas.yview_scroll(int(-2*(event.delta/120)), 'units')))

            widget.checkbutton.bind('<MouseWheel>', (lambda event:
                                                     self.canvas.yview_scroll(int(-2 * (event.delta / 120)), 'units')))

        self.canvas.config(scrollregion=(0, 0, 0, scroll_region_max_y))

    def on_click(self, widget):
        """
        Event handler for left button click.

        :param widget: object of widget that should be affected.
        :return returns nothing.
        """
        if not self.prev_widget:
            self.prev_widget = widget
            widget.refresh_state()
            return

        if widget is self.prev_widget:
            pass
        else:
            self.prev_widget.refresh_state()
            widget.refresh_state()
            self.prev_widget = widget

    def on_double(self, widget):
        """
        Event handler for left button double click.

        :param widget: object of widget that should be affected.
        :return returns nothing.
        """
        pass


class AudioFrame(ttk.Frame):
    """Widget that provide an detail image of audio tags and access to their editing"""
    def __init__(self, parent=None, audio_path=None, style=None, **options):
        """
        Construct a new 'AudioFrame' object using path to directory with mp3 files.

        :param audio_path: string with path to audio file.
        :return returns nothing.
        """
        ttk.Frame.__init__(self, parent, **options)
        self.style = style
        self.cur_img_path = None
        self.cur_img_type = ""
        self.canvas = None
        self.image_chose = None
        self.cur_img_label = None
        self.image_name_holder = None
        self.entries = dict()
        self.audio_path = None
        self.path_to_copy = None
        self.prev_path_to_copy = None
        self.cur_img = None
        self.audio = None

        self.load_audio(audio_path)
        self.make_widget()
        self.load_audio_img()
        self.load_audio_inf()

    def make_widget(self):
        """
        Construct widgets inside 'AudioFrame' object.

        :return returns nothing.
        """
        ttk.Frame(self, height=6).grid(row=0)
        self.make_canvas()
        self.make_path_label()
        self.make_entries()
        self.make_image_menu()
        self.make_lyrics()
        self.make_save_button()

    def make_canvas(self):
        """
        Construct canvas for image inside 'AudioFrame' object.

        :return returns nothing.
        """
        self.canvas = Canvas(self, height=280, width=280, background='white')
        self.canvas.grid(row=1, rowspan=8, columnspan=3, column=0)

    def make_path_label(self):
        """
        Construct label with path to file inside 'AudioFrame' object.

        :return returns nothing.
        """
        path_label = ttk.Label(self, text=self.audio.path.split(sep)[-1], anchor=CENTER, width=10)
        path_label.grid(row=2, column=4, columnspan=3, sticky=EW)

    def make_entries(self):
        """
        Construct entries and related to them labels inside 'AudioFrame' object.

        :return returns nothing.
        """
        row = 4
        for key in supported_tags:
            if key == 'APIC':
                break
            ttk.Frame(self, width=10).grid(row=row, column=4)
            ttk.Label(self, text=supported_tags[key][0].upper() + supported_tags[key][1:], anchor=W, width=10,)\
                .grid(row=row, column=5, sticky=EW)

            entry = Entry(self, width=35)
            entry.grid(row=row, column=6, sticky=EW)

            ttk.Frame(self, width=20).grid(row=row, column=7)

            self.entries[key] = entry
            row += 1
        self.columnconfigure(5, weight=0)
        self.columnconfigure(6, weight=1)

    def make_image_menu(self):
        """
        Construct APIC choose menu inside 'AudioFrame' object.

        :return returns nothing.
        """
        image_menu = ttk.Frame(self)

        self.image_chose = Menubutton(image_menu, text='APIC', width=10, underline=0, bg='white')
        self.image_chose.pack(side=LEFT, expand=YES, fill=BOTH)
        ttk.Button(image_menu, text='Add', command=self.command_add_apic, width=10).\
            pack(side=LEFT, expand=YES, fill=BOTH)
        ttk.Button(image_menu, text='Delete', command=self.command_delete_apic, width=10).\
            pack(side=LEFT, expand=YES, fill=BOTH)
        image_menu.grid(row=10, column=0, columnspan=3, sticky=NSEW)
        self.update_image_menu()

        image_configuration = ttk.Frame(self, height=10)
        ttk.Label(image_configuration, text='Name', width=6).pack(side=LEFT, padx=4)

        self.image_name_holder = Entry(image_configuration)
        self.image_name_holder.pack(side=LEFT, expand=YES, fill=X, padx=3)

        ttk.Button(image_configuration, text='File', command=(lambda: self.command_ask_file())).pack(side=LEFT)
        image_configuration.grid(row=11, column=0, columnspan=3, sticky=NSEW)

        cur_img_label_holder = ttk.Frame(self)
        self.cur_img_label = ttk.Label(cur_img_label_holder, text='No image file selected', anchor=CENTER,
                                       style='ImgFile.TLabel')
        self.cur_img_label.pack(expand=YES, padx=4, fill=X)
        cur_img_label_holder.grid(row=12, column=0, columnspan=3, sticky=NSEW)

    def update_image_menu(self):
        """
        Update APIC choose menu.

        :return returns nothing.
        """
        if self.cur_img_path:
            self.cur_img_label.config(text=self.cur_img_path.split('/')[-1].split(sep)[-1])
        tags = self.audio.get_tag_list()

        for el in tags:
            if isinstance(el, list):
                try:
                    if el[0].startswith('APIC'):
                        menu = Menu(self.image_chose, tearoff=False)
                        for apic_el in el:
                            if apic_el == 'APIC:':
                                type_ = ''
                                menu.add_command(label=apic_el,
                                                 command=(lambda type__=type_: self.load_audio_img(type_=type__)),
                                                 underline=0)
                            else:
                                type_ = apic_el.split(':')[-1]
                                menu.add_command(label=apic_el,
                                                 command=(lambda type__=type_: self.load_audio_img(type_=type__)),
                                                 underline=0)
                        self.image_chose.config(menu=menu)
                        break
                except IndexError:
                    pass

    def load_audio(self, audio_path):
        """
        Load audio from path.

        :return returns nothing.
        """
        try:
            remove(self.prev_path_to_copy)
        except FileNotFoundError:
            pass
        except TypeError:
            pass

        self.audio_path = audio_path
        self.path_to_copy = f'.{sep}temp{sep}copy' + sep + audio_path.split(sep)[-1].split('/')[-1]
        self.prev_path_to_copy = self.path_to_copy

        try:
            remove(self.path_to_copy)
        except FileNotFoundError:
            pass
        copyfile(audio_path, self.path_to_copy)
        self.audio = SimpleMP3(self.path_to_copy)

    def load_audio_img(self, type_=None):
        """
        Set audio APIC to canvas.

        :return returns nothing.
        """
        try:
            if not type_:
                path = self.audio.get_img("./temp/open_img")
            else:
                path = self.audio.get_img("./temp/open_img", img=type_)
                self.cur_img_type = type_
            img = Image.open(path)
            img = img.convert('RGB')
            img.thumbnail((280, 280), Image.ANTIALIAS)
            self.cur_img = PhotoImage(image=img)
            self.canvas.create_image(0, 0, image=self.cur_img, anchor=NW)
            remove(path)
            self.canvas.bind('<1>', (lambda event: self.command_save_img(type_=type_)))

        except TagError:
            img = Image.open(f'.{sep}images{sep}no_image.png')
            img = img.convert('RGB')
            img.thumbnail((280, 280), Image.ANTIALIAS)
            self.cur_img = PhotoImage(image=img)
            self.canvas.create_image(0, 0, image=self.cur_img, anchor=NW)
            self.canvas.unbind('<1>')

    def load_audio_inf(self):
        """
        Set artist, title, number and album to according entries.

        :return returns nothing.
        """
        for key in self.entries:
            if key == 'APIC':
                break
            self.entries[key].delete(0, END)
            if self.audio[supported_tags[key]]:
                self.entries[key].insert(0, str(self.audio[supported_tags[key]]))

    def make_lyrics(self):
        """
        Construct lyrics field.

        :return returns nothing.
        """
        ttk.Label(self, text='Lyrics', width=10).grid(row=11, column=5, padx=3, sticky=EW)
        lyrics = ScrolledText(self, width=29, height=12)
        lyrics.grid(row=11, column=6, rowspan=8, sticky=NSEW)

    def make_save_button(self):
        """
        Construct save button.

        :return returns nothing.
        """
        frame = ttk.Frame(self)
        ttk.Button(frame, text='Save', command=self.command_save).pack(side=RIGHT, padx=5)
        frame.grid(row=19, column=6, pady=5, sticky=EW)

    def command_save(self):
        """
        Save audio changes to current path.

        :return returns nothing.
        """
        for key in self.entries:
            self.audio[supported_tags[key]] = self.entries[key].get()
        copyfile(self.path_to_copy, self.audio_path)
        remove(self.path_to_copy)
        self.load_audio(self.audio_path)
        self.refresh()

    def command_save_as(self, path=None):
        """
        Save audio changes to given path.

        :param path: path to place where should be saved audio.
        :return returns nothing.
        """
        for key in self.entries:
            self.audio[supported_tags[key]] = self.entries[key].get()
        copyfile(self.path_to_copy, path)
        remove(self.path_to_copy)
        self.load_audio(self.audio_path)
        self.refresh()

    def command_add_apic(self):
        """
        Add new APIC tag.

        :return returns nothing.
        """
        if not self.cur_img_path:
            showerror(title='Error occurred', message='Please select an image file')
        else:
            self.audio.set_img(self.cur_img_path, img=self.image_name_holder.get())
            self.update_image_menu()

    def command_delete_apic(self):
        """
        Delete APIC tag.

        :return returns nothing.
        """
        self.audio.del_img(img=self.cur_img_type)
        self.load_audio_img()
        self.update_image_menu()

    def command_ask_file(self):
        """
        Ask for image file, and refresh cur_img_path.

        :return returns nothing.
        """
        self.cur_img_path = askopenfilename(title='Select image file')
        if self.cur_img_path:
            text = self.cur_img_path.split('/')[-1].split(sep)
            self.cur_img_label.config(text=text[-1])
            self.cur_img_label['style'] = 'ImgFileSelected.TLabel'

    def command_save_img(self, type_=None):
        """
        Save img from audio APIC.

        :return returns nothing.
        """
        path = asksaveasfilename(title='Save to...', filetypes=(("", self.audio.get_img_ext(img=type_)),))
        if len(path) == 0:
            return
        self.audio.get_img(path, img=type_)

    def refresh(self):
        """
        Update information about tags audio tags.

        :return returns nothing.
        """
        self.load_audio_img()
        self.load_audio_inf()
        self.update_image_menu()

    def reload(self, audio_path):
        """
        Reload audio from path.

        :param audio_path: path to audio.
        :return returns nothing.
        """
        self.load_audio(audio_path)
        self.make_path_label()
        self.refresh()


class AutoTaggerFrame(ttk.Frame):
    """Widget that provides an interface to auto tagger and its components"""
    def __init__(self, parent=None, iap=None, aap=None, blp=None, cur_dir=None, style='Tagger', **options):
        """
        Construct a new 'AutoTaggerFrame'.

        :param iap: path to image associations file.
        :param aap: path to album associations file.
        :param blp: path to list of banned words/symbols file.
        :param audio_path: string with path to audio file.
        :return returns nothing.
        """
        ttk.Frame.__init__(self, parent, **options)
        self.style = style
        self.image_associations_path = iap
        self.album_associations_path = aap
        self.ban_list_path = blp
        self.cur_dir = cur_dir
        self.buttons_holder = None
        self.stop = None
        self.field = None
        self.row_num = None
        self.auto_tagger = None
        self.start_button = None
        self.stop_button = None

        self.vars = dict()
        self.vars['Title'] = IntVar()
        self.vars['Artist'] = IntVar()
        self.vars['Image'] = IntVar()
        self.vars['Album'] = IntVar()

        self.make_widget()

    def make_widget(self):
        """
        Construct widget content.

        :return returns nothing.
        """
        ttk.Frame(self, height=6, style=self.style + '.TFrame').pack(side=TOP)
        buttons_column = ttk.Frame(self, style='TFrame')
        main_column = ttk.Frame(self, style='TFrame')
        buttons_column.pack(side=LEFT, fill=Y)
        main_column.pack(side=RIGHT, fill=BOTH)
        self.make_menu_column(buttons_column)
        self.make_main_column(main_column)

    def make_menu_column(self, buttons_column):
        """
        Construct main menu column.

        :param buttons_column: holder for buttons.
        :return returns nothing.
        """
        holder = ttk.Frame(buttons_column, style='TFrame')
        holder.pack(side=LEFT, fill=Y)

        buttons_holder = ttk.Frame(holder, style=self.style + '.Left.TFrame')

        ttk.Frame(buttons_holder, width=4).pack(side=LEFT, fill=Y)
        ttk.Frame(buttons_holder, width=4).pack(side=RIGHT, fill=Y)
        ttk.Frame(buttons_holder, width=6, style=self.style + '.Left.TFrame').pack(side=LEFT, fill=Y)
        ttk.Frame(buttons_holder, width=6, style=self.style + '.Left.TFrame').pack(side=RIGHT, fill=Y)

        buttons_holder.pack(side=TOP)

        ttk.Button(buttons_holder, text='Tagger', command=(lambda holder_=holder: self.make_module_menu(holder_)),
                   width=20).pack(side=TOP, fill=X, pady=6)

        ttk.Button(buttons_holder, text='Album',
                   command=(lambda holder_=holder: self.make_module_menu(holder_, module='album'))
                   ).pack(side=TOP, fill=X, pady=2)
        ttk.Button(buttons_holder, text='Image',
                   command=(lambda holder_=holder: self.make_module_menu(holder_, module='image'))
                   ).pack(side=TOP, fill=X)
        ttk.Button(buttons_holder, text='Name', command=self.open_txt)\
            .pack(side=TOP, fill=X, pady=2)

        ttk.Frame(buttons_holder, height=4, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)
        ttk.Frame(holder, height=6, style='TFrame').pack(side=TOP, fill=X)
        ttk.Frame(holder, height=8, style='TFrame').pack(side=BOTTOM, fill=X)

        self.make_module_menu(holder)

    def make_module_menu(self, holder, module='tagger'):
        """
        Construct menu column for selected module.

        :param holder: holder for menu.
        :param module: name of selected module.
        :return returns nothing.
        """
        try:
            self.buttons_holder.destroy()
        except AttributeError:
            pass

        self.buttons_holder = ttk.Frame(holder, style=self.style + '.Left.TFrame')

        ttk.Frame(self.buttons_holder, width=1).pack(side=LEFT, fill=Y)
        ttk.Frame(self.buttons_holder, width=6, style=self.style + '.Left.TFrame').pack(side=LEFT, fill=Y)
        ttk.Frame(self.buttons_holder, width=6, style=self.style + '.Left.TFrame').pack(side=RIGHT, fill=Y)

        self.buttons_holder.pack(side=TOP, expand=YES, fill=Y)

        if module == 'tagger':
            self.make_tagger_menu(self.buttons_holder)
        elif module == 'album':
            self.make_album_menu(self.buttons_holder)
        elif module == 'image':
            self.make_image_menu(self.buttons_holder)

    def make_tagger_menu(self, holder):
        """
        Construct menu for tagger module.

        :param holder: object that hold this menu.
        :return returns nothing.
        """
        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)
        ttk.Frame(holder, width=2, style=self.style + '.Left.TFrame').pack(side=LEFT, fill=Y)
        ttk.Frame(holder, width=3, style=self.style + '.Left.TFrame').pack(side=RIGHT, fill=Y)

        ttk.Label(holder, text="Don't replace", anchor=CENTER, style=self.style + '.Left.TLabel')\
            .pack(side=TOP, fill=X)

        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

        ttk.Checkbutton(holder, text='Title', width=17, var=self.vars['Title'], takefocus=False)\
            .pack(side=TOP, fill=X, pady=2)
        ttk.Checkbutton(holder, text='Artist', var=self.vars['Artist'], takefocus=False)\
            .pack(side=TOP, fill=X)
        ttk.Checkbutton(holder, text='Image', var=self.vars['Image'], takefocus=False)\
            .pack(side=TOP, fill=X, pady=2)
        ttk.Checkbutton(holder, text='Album', var=self.vars['Album'], takefocus=False).pack(side=TOP, fill=X)

        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

    def make_album_menu(self, holder):
        """
        Construct menu for album module.

        :param holder: object that hold this menu.
        :return returns nothing.
        """
        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

        ttk.Label(holder, text="Album associations", anchor=CENTER, style=self.style + '.Left.TLabel') \
            .pack(side=TOP, fill=X)

        ttk.Button(holder, text='Add', command=(lambda: self.command_add('album'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Associate', command=(lambda: self.command_associate('album'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Delete', command=(lambda: self.command_del_association('album'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Show', command=(lambda: self.command_show('album'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Update', command=(lambda: self.command_update('album'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Clear', command=(lambda: self.command_clear('album'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Save', width=20, command=(lambda: self.command_save('album'))) \
            .pack(side=TOP, fill=X)

        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

    def make_image_menu(self, holder):
        """
        Construct menu for image module.

        :param holder: object that hold this menu.
        :return returns nothing.
        """
        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

        ttk.Label(holder, text="Image associations", anchor=CENTER, style=self.style + '.Left.TLabel') \
            .pack(side=TOP, fill=X)

        ttk.Button(holder, text='Add', command=(lambda: self.command_add('img'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Associate', command=(lambda: self.command_associate('img'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Delete', command=(lambda: self.command_del_association('img'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Show', command=(lambda: self.command_show('img'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Update', command=(lambda: self.command_update('img'))) \
            .pack(side=TOP, fill=X, pady=2)
        ttk.Button(holder, text='Clear', command=(lambda: self.command_clear('img'))) \
            .pack(side=TOP, fill=X)
        ttk.Button(holder, text='Save', width=20, command=(lambda: self.command_save('img'))) \
            .pack(side=TOP, fill=X)

        ttk.Frame(holder, height=6, style=self.style + '.Left.TFrame').pack(side=TOP, fill=Y)

    def open_txt(self):
        """
        Open ban list file using system associated program.

        :return returns nothing.
        """
        if sys.platform == 'win32':
            popen(self.auto_tagger.ban_list_path)

    def make_main_column(self, holder):
        """
        Construct console-like field.

        :return returns nothing.
        """
        self.field = ScrolledText(holder, height=28, font='helvetica 10')

        self.field.tag_configure('Info', foreground='green')
        self.field.tag_configure('Error', foreground='#fca117')
        self.field.tag_configure('ErrorCodeRed', foreground='red')

        self.field.pack(side=TOP, padx=5, expand=YES, fill=BOTH)

        self.row_num = 2

        self.auto_tagger = tagger.AutoTagger(self.ban_list_path, self.image_associations_path,
                                             self.album_associations_path, file=self)
        bar = ttk.Frame(holder)
        bar.pack(side=TOP, pady=12, fill=X)
        ttk.Frame(bar, width=20).pack(side=RIGHT)

        self.start_button = ttk.Button(bar, text='Start', width=10, command=self.command_start_tagging)
        self.stop_button = ttk.Button(bar, text='Stop', width=10, command=self.command_stop)
        self.stop_button.pack(side=RIGHT)
        self.start_button.pack(side=RIGHT)

    def command_start_tagging(self):
        """
        Run auto tagger.

        :return returns nothing.
        """
        self.stop = False
        self.start_button['state'] = 'disable'
        self.field.delete('1.0', END)
        self.row_num = 2
        thread = Thread(target=self.command_auto_tag, args=(self.cur_dir,),
                        kwargs={'parent': self})
        thread.start()

    def command_stop(self):
        """
        Stop auto tagger.

        :return returns nothing.
        """
        self.stop = True
        self.start_button['state'] = 'normal'

    def command_auto_tag(self, path, parent=None):
        """
        Auto tagging command.

        :param path: target path for auto tagger.
        :param parent: object which have an stop attribut used to stop tagging.
        :return returns nothing.
        """
        self.auto_tagger.auto_tag(path, replaces=self.vars, parent=parent)
        self.start_button['state'] = 'normal'

    def write(self, text):
        """
        File-like method, write text to field.

        :param text: text which should be written.
        :return returns nothing.
        """
        if text.startswith('[Info]'):
            self.row_num -= 1
            end = f'{self.row_num}.{len(text)}'
            self.field.insert(END, str(text) + '\n')
            self.field.tag_add('Info', f'{self.row_num}.0', end)

        elif text.startswith('[Error]'):
            self.row_num -= 1
            end = f'{self.row_num}.{len(text)}'
            self.field.insert(END, str(text) + '\n')
            self.field.tag_add('Error', f'{self.row_num}.0', end)

        elif text.startswith('[ErrorCodeRed]'):
            self.row_num -= 1
            end = f'{self.row_num}.{len(text)}'
            text = text.replace('ErrorCodeRed', 'Error')
            self.field.insert(END, str(text) + '\n')
            self.field.tag_add('ErrorCodeRed', f'{self.row_num}.0', end)

        elif not text.startswith('\n'):
            self.row_num -= 1
            self.field.insert(END, str(text))
            self.field.insert(END, '\n')

        self.row_num += 1
        self.field.see(END)
        self.field.update()

    def writelines(self, lines):
        """
        File-like method, write lines to field.

        :param lines: lines which should be written.
        :return returns nothing.
        """
        for line in lines:
            self.write(line)

    def command_add(self, assoc_type):
        """
        Add association.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        if assoc_type == 'img':
            win = Toplevel()
            win.title('Add association')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row3 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)
            row3.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='Artist', width=8).pack(side=LEFT, pady=5, padx=3)
            ttk.Label(row3, text='APIC', width=8).pack(side=LEFT, pady=5, padx=3)

            author = ttk.Entry(row1, width=34)
            assoc_name = ttk.Entry(row3, width=34)

            author.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)
            assoc_name.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)

            win.wm_geometry("+%d+%d" % (x, y))
            img = askopenfilename(title='Chose image file')
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type: self.auto_tagger.add_association(
                assoc_type_, author.get(), img=img, assoc_name=assoc_name.get()) or win.destroy())).\
                pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

        elif assoc_type == 'album':
            win = Toplevel()
            win.title('Add association')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row2 = ttk.Frame(win)
            row3 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)
            row2.pack(side=TOP, expand=YES, fill=BOTH)
            row3.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='Artist', width=8).pack(side=LEFT, pady=5, padx=3)
            ttk.Label(row2, text='Title', width=8).pack(side=LEFT, padx=3)
            ttk.Label(row3, text='Album', width=8).pack(side=LEFT, pady=5, padx=3)

            author = ttk.Entry(row1, width=34)
            title = ttk.Entry(row2, width=34)
            album = ttk.Entry(row3, width=34)

            author.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)
            title.pack(side=RIGHT, padx=3, expand=YES, fill=X)
            album.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)

            win.wm_geometry("+%d+%d" % (x, y))
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type: self.auto_tagger.add_association(
                assoc_type_, author.get(), title=title.get(), album=album.get()) or win.destroy()))\
                .pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

    def command_associate(self, assoc_type):
        """
        Make auto associations.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        path = askdirectory()
        if assoc_type == 'img':
            win = Toplevel()
            win.title('Associate')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='APIC', width=8).pack(side=LEFT, padx=3, pady=5)

            type_ = ttk.Entry(row1, width=34)

            type_.pack(side=RIGHT, padx=3, expand=YES, fill=X, pady=5)

            win.wm_geometry("+%d+%d" % (x, y))
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type, path_=path: self.auto_tagger.
                                                     associate(assoc_type_, path_, type_=type_.get(), file=self)
                                                     or win.destroy())).pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

        elif assoc_type == 'album':
            win = Toplevel()
            win.title('Associate')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='Album', width=8).pack(side=LEFT, padx=3, pady=5)

            album = ttk.Entry(row1, width=34)

            album.pack(side=RIGHT, padx=3, expand=YES, fill=X, pady=5)

            win.wm_geometry("+%d+%d" % (x, y))
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type, path_=path: self.auto_tagger.
                                                     associate(assoc_type_, path_, album=album.get(), file=self)
                                                     or win.destroy())).pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

    def command_del_association(self, assoc_type):
        """
        Delete association association.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        if assoc_type == 'img':
            win = Toplevel()
            win.title('Delete association')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row2 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)
            row2.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='Artist', width=8).pack(side=LEFT, pady=5, padx=3)
            ttk.Label(row2, text='APIC', width=8).pack(side=LEFT, padx=3)

            author = ttk.Entry(row1, width=34)
            assoc_name = ttk.Entry(row2, width=34)

            author.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)
            assoc_name.pack(side=RIGHT, padx=3, expand=YES, fill=X)

            win.wm_geometry("+%d+%d" % (x, y))
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type: self.auto_tagger.del_association(
                assoc_type_, author.get(), assoc_name=assoc_name.get()) or win.destroy()))\
                .pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

        elif assoc_type == 'album':
            win = Toplevel()
            win.title('Delete association')
            x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
            y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
            row1 = ttk.Frame(win)
            row2 = ttk.Frame(win)
            row1.pack(side=TOP, expand=YES, fill=BOTH)
            row2.pack(side=TOP, expand=YES, fill=BOTH)

            ttk.Label(row1, text='Artist', width=8).pack(side=LEFT, pady=5, padx=3)
            ttk.Label(row2, text='Title', width=8).pack(side=LEFT, padx=3)

            author = ttk.Entry(row1, width=34)
            title = ttk.Entry(row2, width=34)

            author.pack(side=RIGHT, pady=5, padx=3, expand=YES, fill=X)
            title.pack(side=RIGHT, padx=3, expand=YES, fill=X)

            win.wm_geometry("+%d+%d" % (x, y))
            ttk.Button(win, text='Perform', command=(lambda assoc_type_=assoc_type: self.auto_tagger.del_association(
                assoc_type_, author.get(), title=title.get()) or win.destroy()))\
                .pack(side=RIGHT, pady=5, padx=3)
            win.focus_set()
            win.grab_set()
            win.wait_window()

    def command_show(self, assoc_type):
        """
        Print associations to field.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        self.field.delete('1.0', END)
        if assoc_type == 'img':
            associations = self.auto_tagger.get_associations(assoc_type)
            print('-' * 116, file=self)
            try:
                print(associations[0][0], file=self)
            except IndexError:
                return
            print(' ', file=self)
            print(f'{associations[0][1]} - {associations[0][2]}', file=self)
            last_group = associations[0][0]
            for i in range(1, len(associations)):
                if last_group == associations[i][0]:
                    pass
                else:
                    print('-' * 116, file=self)
                    print(associations[i][0], file=self)
                    print(' ', file=self)
                    last_group = associations[i][0]
                print(f'{associations[i][1]} - {associations[i][2]}', file=self)

        elif assoc_type == 'album':
            associations = self.auto_tagger.get_associations(assoc_type)
            print('-' * 116, file=self)
            try:
                print(associations[0][0], file=self)
            except IndexError:
                return
            print(' ', file=self)
            print(f'{associations[0][1]} - {associations[0][2]}', file=self)
            last_group = associations[0][0]
            for i in range(1, len(associations)):
                if last_group == associations[i][0]:
                    pass
                else:
                    print('-' * 116, file=self)
                    print(associations[i][0], file=self)
                    print(' ', file=self)
                    last_group = associations[i][0]
                print(f'{associations[i][1]} - {associations[i][2]}', file=self)

    def command_update(self, assoc_type):
        """
        Update associations.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        path = askopenfilename(title='Chose update file')
        try:
            if path:
                self.auto_tagger.update_associations(assoc_type, path)
        finally:
            pass

    def command_clear(self, assoc_type):
        """
        Clear associations.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        self.auto_tagger.clear_associations(assoc_type)

    def command_save(self, assoc_type):
        """
        Save associations.

        :param assoc_type: type of association.
        :return returns nothing.
        """
        self.auto_tagger.save_associations(assoc_type)
