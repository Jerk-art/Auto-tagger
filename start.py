"""This module link up widgets and files, and start program."""


from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from GUI import AudioFrame
from GUI import FileSection
from GUI import AutoTaggerFrame
from GUI import LoadingFrame
from threading import Thread
from os import sep, listdir


class GUILoadingFrame(LoadingFrame):
    """Class that inherits LoadingFrame and provide some mechanisms to link it with other widgets."""
    def __init__(self, parent=None, style=None, styles=None, **options):
        """
        Construct a new 'GUILoadingFrame'.

        :return returns nothing.
        """
        LoadingFrame.__init__(self, parent=parent, style=style, **options)
        self.win = None
        self.target = None
        self.styles = styles

    def command_open(self):
        """
        Open folder and load interface.

        :return returns nothing.
        """
        open_ = False
        for el in listdir(self.folder):
            if el.endswith('.mp3'):
                open_ = True
                break
        if not open_:
            self.label.config(text='There is no mp3')
            return
        if not self.target:
            self.target = self.load_file_section
        LoadingFrame.command_open(self)
        thread = Thread(target=self.target)
        thread.start()

    def load_file_section(self):
        """
        Load GUIFileSection, and stop current mainloop.

        :return returns nothing.
        """
        global file_section
        file_section = GUIFileSection(self.win, dir_=self.folder, styles=self.styles)
        self.destroy()
        self.win.quit()


class GUILoadingWindow(Toplevel):
    """Provide Toplevel window with LoadingFrame inside."""
    def __init__(self, style=None, styles=None, **options):
        """
        Construct a new 'GUILoadingWindow'.

        :return returns nothing.
        """
        Toplevel.__init__(self, **options)
        self.frame = GUILoadingFrame(self, style=style, styles=styles)
        self.frame.target = self.load_folder
        self.frame.pack()
        self.win = None
        self.styles = styles

    def load_folder(self):
        """
        Reload GUIFileSection.

        :return returns nothing.
        """
        global file_section
        global audio_frame
        global tagger_frame
        tagger_frame.cur_dir = self.frame.folder
        new_file_section = GUIFileSection(self.win, dir_=self.frame.folder, styles=self.styles)
        file_section.destroy()
        file_section = new_file_section
        file_section.pack(side=RIGHT, fill=Y)
        audio_frame.reload(file_section.first_file)
        self.destroy()


class GUIFileSection(FileSection):
    """Class that inherits FileSection and provide some mechanisms to link it with other widgets."""
    def __init__(self, parent=None, dir_='', styles=None, **options):
        """
        Construct a new 'GUIFileSection'.

        :return returns nothing.
        """
        FileSection.__init__(self, parent=parent, dir_=dir_, styles=styles, width=300, **options)
        self.audio_frame = None

    def on_double(self, widget):
        """
        Load file to audio frame.

        :return returns nothing.
        """
        global tagger_frame
        global audio_frame

        audio_frame.reload(widget.file.path)
        tagger_frame.pack_forget()
        audio_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)


class GUIAudioFrame(AudioFrame):
    """Class that inherits AudioFrame and provide some mechanisms to link it with other widgets."""
    def __init__(self, parent=None, audio_path=None, style=None, **options):
        """
        Construct a new 'GUIAudioFrame'.

        :return returns nothing.
        """
        AudioFrame.__init__(self, parent=parent, audio_path=audio_path, style=style, **options)
        self.file_section = None
        self.is_cur_dir = None

    def command_save(self):
        """
        Save changes in audio tags.

        :return returns nothing.
        """
        if self.is_cur_dir:
            AudioFrame.command_save(self)
            file_section.files[self.audio_path.split(sep)[-1].split('/')[-1]].refresh()
        else:
            AudioFrame.command_save(self)

    def command_save_as(self, path=None):
        """
        Save changes in audio tags to path.

        :param path: sting with path where should be saved audio
        :return returns nothing.
        """
        path = asksaveasfilename(title='Save to...', filetypes=(("MPEG", 'mp3'),))
        if len(path) == 0:
            return
        path += '.mp3'
        AudioFrame.command_save_as(self, path=path)

    def reload(self, file_path, is_cur_dir=True):
        """
        Reload audio frame using file from file_path.

        :param file_path: path to file.
        :param is_cur_dir: is current dir or not(Bool).
        :return returns nothing.
        """
        AudioFrame.reload(self, file_path)
        self.is_cur_dir = is_cur_dir


class GUIAutoTaggerFrame(AutoTaggerFrame):
    """Class that inherits AutoTaggerFrame and provide some mechanisms to link it with other widgets."""
    def __init__(self, parent=None, iap=None, aap=None, blp=None, cur_dir=None, style='Tagger', styles=None, **options):
        AutoTaggerFrame.__init__(self, parent=parent, iap=iap, aap=aap, blp=blp, cur_dir=cur_dir, style=style,
                                 **options)
        self.win = None
        self.styles = styles

    def command_auto_tag(self, path, parent=None):
        """
        Run auto tagging and reload file section.

        :return returns nothing.
        """
        AutoTaggerFrame.command_auto_tag(self, path, parent=parent)

        global file_section
        new_file_section = GUIFileSection(self.win, dir_=self.cur_dir, styles=self.styles)
        file_section.destroy()
        file_section = new_file_section
        file_section.pack(side=RIGHT, fill=Y)


class MenuBar(ttk.Frame):
    """Provide menu bar."""
    def __init__(self, parent=None, style='menu.TFrame', **options):
        """
        Construct a new 'MenuBar'.

        :return returns nothing.
        """
        ttk.Frame.__init__(self, parent, style=style, **options)

        empty_space = Frame(self)
        delimiter = Frame(empty_space, height=1, bg='grey')
        delimiter.pack(side=TOP, fill=X)

        but1 = Menubutton(self, text='File', width=10, bg='white', activebackground='#f0f0f0', bd=1,
                          highlightbackground='grey', highlightthickness=1, highlightcolor='white')
        menu = Menu(but1, tearoff=False)
        menu.add_command(label='Open', command=self.command_open, underline=0)
        menu.add_command(label='Save as', command=self.command_save_as, underline=0)
        but1.config(menu=menu)
        but1.pack(side=LEFT)

        but2 = Menubutton(self, text='Directory', width=10, bg='white', activebackground='#f0f0f0', bd=1,
                          highlightbackground='grey', highlightthickness=1, highlightcolor='white')
        menu = Menu(but2, tearoff=False)
        menu.add_command(label='Open', command=command_open_folder, underline=0)
        but2.config(menu=menu)
        but2.pack(side=LEFT)

        but3 = Menubutton(self, text='Regime', width=10, bg='white', activebackground='#f0f0f0', bd=1,
                          highlightbackground='grey', highlightthickness=1, highlightcolor='white')

        menu = Menu(but3, tearoff=False)
        menu.add_command(label='Manually', command=(lambda: self.command_set_regime('manually')), underline=0)
        menu.add_command(label='Auto', command=(lambda: self.command_set_regime('auto')), underline=0)
        but3.config(menu=menu)

        but3.pack(side=LEFT)

        empty_space.pack(side=LEFT, expand=YES, fill=BOTH)

        self.audio_frame = None

    def command_set_regime(self, regime):
        """
        Set current regime(manually or auto tagging).

        :return returns nothing.
        """
        global audio_frame
        global tagger_frame

        if regime == 'manually':
            tagger_frame.pack_forget()
            audio_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
        elif regime == 'auto':
            audio_frame.pack_forget()
            tagger_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)

    def command_open(self):
        """
        Open audio file and reload AudioFrame

        :return returns nothing.
        """
        file_path = askopenfilename(title='File to open', filetypes=[("MPEG", ".mp3")])
        self.audio_frame.reload(file_path, is_cur_dir=False)

        global tagger_frame
        global audio_frame

        tagger_frame.pack_forget()
        audio_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)

    def command_save_as(self):
        """
        Save file as.

        :return returns nothing.
        """
        self.audio_frame.command_save_as()


def command_open_folder():
    """
    Create new window to choose folder with audio.

    :return returns nothing.
    """
    win = GUILoadingWindow(style='LoadingWindow', styles=styles)
    x = (win.winfo_screenwidth() - win.winfo_reqwidth() - 280) / 2
    y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
    win.wm_geometry("+%d+%d" % (x, y))
    win.win = root
    win.focus_set()
    win.grab_set()
    win.wait_window()


if __name__ == "__main__":
    root = Tk()
    root.title('mTool')
    style = ttk.Style()

    # LoadingWindow style configuration
    style.map('LoadingWindow.TFrame', background=[("", 'white')])
    style.map('LoadingWindow.TLabel', background=[("", 'white')])

    # File Pair style configuration
    style.map('File.Pair.TCheckbutton',
              background=[('!active', '#e3e1de'), ('active', '#e3e1de')],
              relief=[('!active', FLAT), ('active', FLAT)])
    style.configure('File.Pair.Canvas', bg='#e3e1de')

    style.map('File.Pair.Active.TCheckbutton',
              background=[('!active', '#94d1a4'), ('active', '#94d1a4')],
              indicatorrelief=[('!active', '#94d1a4'), ('active', '#94d1a4')])
    style.configure('File.Pair.Active.Canvas', bg='#94d1a4')

    # File Odd style configuration
    style.map('File.Odd.TCheckbutton',
              background=[('!active', 'white'), ('active', 'white')],
              indicatorrelief=[('!active', 'white'), ('active', 'white')])
    style.configure('File.Odd.Canvas', bg='white')

    style.map('File.Odd.Active.TCheckbutton',
              background=[('!active', '#94d1a4'), ('active', '#94d1a4')],
              indicatorrelief=[('!active', '#94d1a4'), ('active', '#94d1a4')])
    style.configure('File.Odd.Active.Canvas', bg='#94d1a4')

    styles = ['File.Pair', 'File.Odd']

    # AudioFrame style configuration
    style.map('TEntry',
                  bordercolor=[('active', 'green')],
                  borderwidth=[('focus', 5)],
                  relief=[('!pressed', FLAT), ('pressed', FLAT)],
                  fieldbackground=[("!disabled", "green3")],)
    style.configure('TEntry', borderwidth=15, fieldbackground="green3")
    style.map('ImgFile.TLabel', background=[("", '#ffa963')])
    style.map('ImgFileSelected.TLabel', background=[("", '#94d1a4')])
    style.map('colored.TFrame', background=[("", '#94d1a4')])

    # Tagger style configuration
    style.map('Tagger.Left.TFrame', background=[("", 'white')])
    style.map('Tagger.Left.TLabel', background=[("", 'white')])
    style.map('Tagger.TCheckbutton', background=[("", 'white')])
    style.map('Tagger.colored.TFrame', background=[("", '#94d1a4')])
    style.map('Tagger.TFrame', background=[("", '#f0f0f0')])

    global file_section

    loading_frame = GUILoadingFrame(root, style='LoadingWindow', styles=styles)
    loading_frame.win = root
    loading_frame.pack()

    x = (root.winfo_screenwidth() - root.winfo_reqwidth() - 280) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.wm_geometry("+%d+%d" % (x, y))

    # wait for user choose directory
    root.mainloop()

    holder = Frame(root)
    menu_bar = MenuBar(holder)

    audio_frame = GUIAudioFrame(holder, audio_path=file_section.first_file, style=style)

    path = '.' + sep + 'auto' + sep + 'auto tagger files' + sep
    iap = path + 'imgs'
    aap = path + 'albums'
    blp = path + 'banlist.txt'

    tagger_frame = GUIAutoTaggerFrame(holder, iap=iap, aap=aap, blp=blp, cur_dir=loading_frame.folder, styles=styles)
    tagger_frame.win = root

    audio_frame.file_section = file_section
    menu_bar.audio_frame = audio_frame
    file_section.audio_frame = audio_frame

    menu_bar.pack(side=TOP, fill=X)
    audio_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
    tagger_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)
    tagger_frame.pack_forget()
    holder.pack(side=LEFT, expand=YES, fill=BOTH)
    file_section.pack(side=RIGHT, fill=Y)
    audio_frame.focus_set()

    x = (root.winfo_screenwidth() - 962) / 2
    y = (root.winfo_screenheight() - 582) / 2
    root.geometry('1062x582')
    root.wm_geometry("+%d+%d" % (x, y))

    root.mainloop()
