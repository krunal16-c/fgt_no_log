"""
File Name: main_window.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: The main window for the application.

"""

import tkinter as tk
import base64

import threading

from tkinter import ttk
from io import BytesIO

from PIL import Image
from PIL import ImageTk as itk

from friendly_ground_truth.view.fgt_canvas import FGTCanvas
from friendly_ground_truth.view.info_panel import InfoPanel
from friendly_ground_truth.view.help_dialogs import (AboutDialog,
                                                     KeyboardShortcutDialog)
from friendly_ground_truth.view.preferences_window import PreferencesWindow
from friendly_ground_truth.view.preview_window import (PreviewFrame,
                                                       PreviewWindow)
from functools import partial

import logging
module_logger = logging.getLogger('friendly_gt.view')


class MainWindow(ttk.Frame):
    """
    The main window for the application.

    Attributes:
        {% An Attribute %}: {% Description %}
    """

    def __init__(self, master, controller):
        """
        Initialize the main window.

        Args:
            master: The root tkinter process.
            controller: The controller logic

        Returns:
            A main window object.
        """

        self._preview_window = None
        self._cur_preview_thread = None

        preferences = controller.load_preferences()

        self._preferences = preferences

        theme = preferences['theme']

        if theme == 'Light':
            self._darkmode = False
        elif theme == 'Dark':
            self._darkmode = True

        if self._darkmode:
            from friendly_ground_truth.view import dark_theme

            dark_theme.style.theme_use("dark_theme")
            self.style = dark_theme.style

        else:
            from friendly_ground_truth.view import light_theme
            light_theme.style.theme_use("light_theme")
            self.style = light_theme.style

        ttk.Frame.__init__(self, master=master, style="Main.TFrame")

        # --------------------------------------
        # Private Attributes
        # --------------------------------------

        # The parent tkinter object
        self._master = master
        # The controller for this window
        self._controller = controller

        # For logging
        self._logger = logging.getLogger('friendly_gt.view.MainWindow')

        # The canvas used to display and interact with images
        self._canvas = None

        # The previous state of the keyboard
        self._previous_state = 0

        # Mappings from tool id to keyboard shortcut
        self._key_mappings = {}
        # Mappings from keyboard shortcut to tool id
        self._reverse_key_mappings = {}

        # Tkinter menu objects
        self._menubar = None
        self._filemenu = None
        self._helpmenu = None

        # Toolbar
        self._toolbar = None
        # id -> button mapping
        self._toolbar_buttons = {}
        # The colour of a default button
        self._orig_button_colour = None
        # The label displaying the path to the current image
        self._image_indicator = None

        self._old_tool_id = None
        # The previous image
        self._old_img = None

        self._old_tool = None
        # --------------------------------------

        self._master.title("Friendly Ground Truth")
        self._master.columnconfigure(0, weight=1)

        self._master.grid_rowconfigure(0, weight=0)
        self._master.grid_rowconfigure(1, weight=1)

        self._set_master_theme()

        self._register_key_mappings()

        self._create_menubar()

        # Interactions
        self.bind_all('<Key>', self._keystroke)
        # Mousewheel for Windows and Mac
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        # Mousewheel for Linux
        self.bind_all("<Button-5>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)

        self._info_panel = InfoPanel(self.master)
        self._info_panel.config(style="InfoPanel.TFrame")

        self._info_panel.grid(row=2, column=0, sticky='ew', columnspan=2)

        if self._darkmode:
            self._enable_darkmode_buttons()
    # ==========================================================
    # PUBLIC FUNCTIONS
    # ==========================================================

    def create_canvas(self, image):
        """
        Create the image canvas.

        Args:
            image: The image, a numpy array.

        Returns:
            None

        Postconditions:
            self._canvas is set
        """
        if self._canvas is not None:
            self._canvas.destroy()

        self._canvas = FGTCanvas(self.master, image, self, self.style)
        self._canvas.grid(row=1, column=0, sticky="NSEW")

        self._on_preview_setting()

    def set_theme(self, theme):
        """
        Set the current theme for the application.

        Args:
            theme: A string.

        Returns:
            None
        """

        if theme.lower() == 'dark':
            self._darkmode = True

            from friendly_ground_truth.view import dark_theme

            dark_theme.style.theme_use("dark_theme")
            self.style = dark_theme.style

            self._enable_darkmode_buttons()

        elif theme.lower() == 'light':
            self._darkmode = False
            from friendly_ground_truth.view import light_theme

            light_theme.style.theme_use("light_theme")
            self.style = light_theme.style

            self._toolbar.destroy()
            self._create_toolbar()

        self._set_menubar_theme()
        self._set_helpmenu_theme()
        self._set_viewmenu_theme()
        self._set_master_theme()
        self._set_filemenu_theme()

        self._canvas.set_theme(self.style)

        if self._preview_window is not None:
            self._preview_window.set_theme(self.style)

    def start_progressbar(self, num_patches):
        """
        Start displaying a progressbar.

        Args:
            num_patches: The number of patches that are being loaded.

        Returns:
            None

        Postconditions:
            A progressbar window is opened and initialized
        """
        self.progress_popup = tk.Toplevel()
        self.progress_popup.geometry("100x50+500+400")

        frame = ttk.Frame(self.progress_popup)

        ttk.Label(frame, text="Image Loading.")\
            .grid(row=0, column=0)

        self.load_progress = 0
        self.load_progress_var = tk.DoubleVar()
        self.load_progress_bar = ttk.Progressbar(frame,
                                                 variable=self.
                                                 load_progress_var,
                                                 maximum=100)

        self.load_progress_bar.grid(row=1, column=0, sticky="NSEW")

        self.progress_step = float(100.0/num_patches)

        frame.grid(row=0, column=0, sticky="NSEW")
        self.progress_popup.grid_columnconfigure(0, weight=1)

        self.progress_popup.pack_slaves()

        background = self.style.lookup("TFrame", "background")
        self.progress_popup.config(background=background)

    def show_image(self, img, new=False, patch_offset=(0, 0)):
        """
        Display the given image on the canvas.

        Args:
            img: The image to display, a numpy array
            new: Whether to reset the canvas for a new image
            patch_offset: The offset of the current patch in the context image
        Returns:
            None

        Postconditions:
            The canvas's image will be set to the image.
        """

        if self._canvas is None:
            self.create_canvas(img)
            return
        elif new:
            self._canvas.new_image(img, patch_offset=patch_offset)

            t = threading.Thread(target=self.update_preview, name="preview")
            t.daemon = True
            t.start()

        else:

            self._canvas.set_image(img)

            if self._cur_preview_thread is not None:
                self._cur_preview_thread.cancel()

            self._cur_preview_thread = threading.Timer(1.0,
                                                       self.update_preview)
            self._cur_preview_thread.daemon = True
            self._cur_preview_thread.start()

    def update_preview(self):

        if self._preview_window is not None:
            img = self._controller.get_image_preview()

            self._preview_window.update_image(img)

    def on_canvas_click(self, pos):
        """
        Called when the canvas has a click event.

        Args:
            pos: The position of the event.

        Returns:
            None
        """
        self._controller.click_event(pos)

    def on_canvas_drag(self, pos, drag_id=None):
        """
        Called when the canvas has a drag event.

        Args:
            pos: The position of the drag.
            drag_id: Idenitifier for unique drag events.

        Returns:
            None
        """
        self._controller.drag_event(pos, drag_id=drag_id)

    def set_canvas_cursor(self, cursor):
        """
        Set the cursor for the canvas.

        Args:
            cursor: The cursor string.

        Returns:
            None

        Postconditions:
            The canvas' cursor will be set.
        """
        self._canvas.cursor = cursor

    def set_canvas_brush_size(self, radius):
        """
        Set the size of the brush in the canvas.

        Args:
            radius: The radius to draw the brush.

        Returns:
            None

        Postconditions:
            The canvas' brush size is changed.
        """
        self._canvas.brush_radius = radius

    def update_canvas_image(self, image):
        """
        Set the current image in the canvas.

        Args:
            image: The image, a numpy array

        Returns:
            None

        Postconditions:
            The canvas's image will be set to the given image data.
        """
        if self._canvas is not None:
            self._canvas.img = image

    def update_info_panel(self, tool):
        """
        Update the info panel with the activated tool's widget.

        Args:
            tool: The tool that the info panel should represent.

        Returns:
            None

        Postconditions:
            The info panel will display the widget defined by the tool.
        """
        tool.lock_undos()
        if self._old_tool is not None:
            self._old_tool.destroy_info_widget()

        self._info_panel.set_info_widget(tool.
                                         get_info_widget(self._info_panel,
                                                         self.style),
                                         tool.name)

        self._old_tool = tool

    def enable_button(self, id):
        """
        Enable the button with the given id.

        Args:
            id: The id of the tool whose button to enable.

        Returns:
            None

        Postconditions:
            The button will be in the enabled state.
        """
        self._toolbar_buttons[id].config(state='normal')

    def disable_button(self, id):
        """
        Disable the button with the given id.

        Args:
            id: The id of the tool whose button to disable.

        Returns:
            None

        Postconditions:
            The button will be in the disabled state.
        """
        self._toolbar_buttons[id].config(state='disabled')

    def update_image_indicator(self, text):
        """
        Update the image indicator in the toolbar with the given text.

        Args:
            text: The text to display in the toolbar.

        Returns:
            None

        Postconditions:
            The text in the toolbar will display the given text.
        """
        self._image_indicator.config(text=text)

    def log_mouse_event(self, pos, event, button):
        self._controller.log_mouse_event(pos, event, button)

    def log_drag_event(self, drag_type, start_pos, end_pos):
        self._controller.log_drag_event(drag_type, start_pos, end_pos)

    def log_zoom_event(self, zoom_factor):
        self._controller.log_zoom_event(zoom_factor)

    def set_default_tool(self, id):
        self._update_toolbar_state(id)

    # ==========================================================
    # PRIVATE FUNCTIONS
    # ==========================================================

    def _create_menubar(self):
        """
        Create the menu bar.


        Returns:
            None

        Postconditions:
            The menu bar will be created at the top of the screen.
        """

        self._menubar = tk.Menu(self.master)

        self._set_menubar_theme()

        self._create_file_menu()

        self._create_view_menu()

        self._create_help_menu()

        self._create_toolbar()

        self._master.config(menu=self._menubar)

    def _create_file_menu(self):
        """
        Create the file menu.


        Returns:
            None

        Postconditions:
            The file menu will be populated.
        """

        self._filemenu = tk.Menu(self._menubar, tearoff=0)

        self._set_filemenu_theme()

        self._filemenu.add_command(label="Load Image",
                                   command=self._on_load_image)

        self._filemenu.add_command(label="Save Mask",
                                   command=self._on_save_mask)

        self._filemenu.add_separator()

        self._filemenu.add_command(label="Load Existing Mask",
                                   command=self._on_load_mask)

        self._filemenu.add_separator()
        self._filemenu.add_command(label="Preferences",
                                   command=self._on_preferences)

        self._menubar.add_cascade(label="File", menu=self._filemenu)

    def _create_view_menu(self):
        """
        Create the view menu.


        Returns:
            None

        Postconditions:
            The view menu will be populated.
        """
        if "preview" not in self._preferences.keys():
            preview_pref = 1
        else:
            preview_pref = self._preferences['preview']

        self._viewmenu = tk.Menu(self._menubar, tearoff=0)

        self._preview_setting = tk.IntVar()
        self._preview_setting.set(preview_pref)

        submenu = tk.Menu(self._menubar)
        submenu.add_radiobutton(label="Docked", value=1,
                                variable=self._preview_setting,
                                command=self._on_preview_setting)

        submenu.add_radiobutton(label="Floating", value=2,
                                variable=self._preview_setting,
                                command=self._on_preview_setting)

        submenu.add_radiobutton(label="Hidden", value=3,
                                variable=self._preview_setting,
                                command=self._on_preview_setting)

        self._previewmenu = submenu

        self._set_viewmenu_theme()

        self._menubar.add_cascade(label="View", menu=self._viewmenu)
        self._viewmenu.add_cascade(label="Preview", menu=submenu)

    def _on_preview_setting(self):
        """
        Called when the user changes the preview window settings.


        Returns:
            None
        """

        # Set to docked
        if self._preview_setting.get() == 1:
            self._dock_preview()
        # Set to floating
        elif self._preview_setting.get() == 2:
            self._float_preview()
        # Set to hidden
        else:
            self._hide_preview()

        self._preferences['preview'] = self._preview_setting.get()

        self._controller.save_preferences(self._preferences)

    def _dock_preview(self):

        if self._preview_window is not None:
            self._preview_window.destroy()

        self._preview_window = PreviewFrame(self.master,
                                            self._controller
                                            .get_image_preview(),
                                            self._controller, self.style)

        self._preview_window.grid(row=1, column=1, sticky="NSEW")

        self._master.grid_rowconfigure(0, weight=0)
        self._master.grid_rowconfigure(1, weight=1)

        self._master.grid_columnconfigure(0, weight=3)
        self._master.grid_columnconfigure(1, weight=1)

    def _float_preview(self):

        if self._preview_window is not None:
            self._preview_window.destroy()

        self._preview_window = PreviewWindow(self._controller
                                             .get_image_preview(),
                                             self._controller, self.style)

        self._master.grid_columnconfigure(0, weight=1)
        self._master.grid_columnconfigure(1, weight=0)

    def _hide_preview(self):

        if self._preview_window is not None:
            self._preview_window.destroy()

        self._master.grid_columnconfigure(0, weight=1)
        self._master.grid_columnconfigure(1, weight=0)

        self._preview_window = None

    def _create_help_menu(self):
        """
        Create the help menu.


        Returns:
            None

        Postconditions:
            The help menu will be populated.
        """

        self._helpmenu = tk.Menu(self._menubar, tearoff=0)

        self._set_helpmenu_theme()

        self._helpmenu.add_command(label="About",
                                   command=self._on_about)

        self._helpmenu.add_command(label="Keyboard Shortcuts",
                                   command=self._on_keyboard_shortcuts)

        self._menubar.add_cascade(label="Help", menu=self._helpmenu)

    def _create_tool_tip(self, button, id, name):
        """
        Create a tool tip for the given button.

        Args:
            button: The button to create the tooltip for.
            id: The id of the tool.
            name: The name of the tool
        Returns:
            None

        Postcondition:
            The tooltip is attached to the button.
        """
        key = self._key_mappings[id]

        tip = name + "(" + key + ")"

        CreateToolTip(button, tip)

    def _create_toolbar(self):
        """
        Create the toolbar.


        Returns:
            None

        Postconditions:
            The toolbar is created.
        """

        self._toolbar = ttk.Frame(self._master, style="Toolbar.TFrame")

        # Create image interaction tools
        image_tools = self._controller.image_tools

        group_priorities = [(0, "Markups"), (1, "Navigation"), (2, "Undo")]

        groups = [[] for _ in group_priorities]
        groups.append([])

        for tool_id in image_tools.keys():
            tool = image_tools[tool_id]

            tool_group = tool.group

            in_priors = False

            for p in group_priorities:
                if tool_group == p[1]:
                    groups[p[0]].append(tool)
                    in_priors = True
                    continue

            if not in_priors:
                groups[-1].append(tool)

        if len(groups[-1]) == 0:
            groups.pop()

        column = 0
        for group in groups:
            for tool in group:
                icon = self._load_icon_from_string(tool.icon_string)
                command = partial(self._on_tool_selected, tool.id)

                if tool.persistant:
                    button_style = "PersistantToolbar.TButton"
                else:
                    button_style = "Toolbar.TButton"

                button = ttk.Button(self._toolbar, image=icon,
                                    style=button_style,
                                    command=command)

                button.image = icon
                button.pack(side="left", padx=2, pady=2)
                # button.grid(column=column, row=0, sticky='EW')
                column += 1

                self._create_tool_tip(button, tool.id, tool.name)
                self._toolbar_buttons[tool.id] = button

            sep = tk.ttk.Separator(self._toolbar, orient="vertical",
                                   style="TSeparator")
            sep.pack(side='left', padx=5, fill='both')

        self._image_indicator = ttk.Label(self._toolbar,
                                          text="No Image Loaded",
                                          style="Toolbar.TLabel")

        self._image_indicator.pack(side='right', padx=2, pady=2)
        self._toolbar.grid(column=0, row=0, sticky='NEW', columnspan=2)

    def _enable_darkmode_buttons(self):
        """
        Switch the icons for the buttons to dark mode.


        Returns:
            None
        """
        for key in self._toolbar_buttons:
            tool = self._controller.image_tools[key]
            button = self._toolbar_buttons[key]

            icon = self._load_icon_from_string(tool.darkmode_icon_string)

            button.config(image=icon)
            button.image = icon

    def _keystroke(self, event):
        """
        Called when the keybord is used.

        Args:
            event: The keyboard event.

        Returns:
            None

        Postconditions:
            The canvas is modified according to the key pressed.
        """
        key = ''

        # means that the Control key is pressed
        if event.state - self._previous_state == 4:
            key = "CTRL+"
        else:
            # remember the last keystroke state
            self._previous_state = event.state

        key += event.keysym.lower()

        self._logger.debug("KEY: " + key)

        if key == "CTRL+equal" or key == "CTRL+=":
            self._controller.adjust_tool(1)
        elif key == "CTRL+minus" or key == "CTRL+-":
            self._controller.adjust_tool(-1)
        elif key == "f11":
            self._master.attributes('-fullscreen', True)
        elif key == "escape":
            self._master.attributes('-fullscreen', False)
        else:
            try:
                tool_id = self._reverse_key_mappings[key]
                self._on_tool_selected(tool_id)
            except KeyError:
                self._logger.debug("{} is not a valid key code".format(key))

    def _load_icon_from_string(self, icon_string):
        """
        Load a tkinter compatible image from an icon bytestring.

        Args:
            icon_string: The 64 bit encoded icon string

        Returns:
            A ImageTK PhotoImage
        """
        data = Image.open(BytesIO(base64.b64decode(icon_string)))
        img = itk.PhotoImage(data)

        return img

    def _on_load_image(self):
        """
        Called when the load image button is chosen


        Returns:
            None

        Postconditions:
            The controllers Image property is set
        """
        self._controller.load_new_image()
        self._old_img = None

    def _on_load_mask(self):
        """
        Called when the load existing mask button is chosen.


        Returns:
            None
        """

        self._controller.load_existing_mask()

    def _on_save_mask(self):
        """
        Called when the save mask button is chosen

        Returns:
            None

        Postcondition:
            The controller will be called to save the mask.

        Returns:
            None
        """
        self._controller.save_mask()

    def _on_preferences(self):
        """
        Called when the preferences menu option is chosen.


        Returns:
            None
        """
        PreferencesWindow(self._controller, self.style)

    def _on_about(self):
        """
        Called when the about button is chosen.


        Returns:
            None
        """
        AboutDialog()

    def _on_keyboard_shortcuts(self):
        """
        Called when the keyboard shortcuts button is chosen/


        Returns:
            None
        """
        KeyboardShortcutDialog(self._controller.image_tools, self._darkmode)

    def _on_tool_selected(self, id):
        """
        Called when a tool is selected in the menubar

        Args:
            id: The id of the tool.

        Returns:
            None

        Postconditions:
            The controller is updated to reflect the current chosen tool.
        """
        self._controller.activate_tool(id)
        self._update_toolbar_state(id)

    def _register_key_mappings(self):
        """
        Register a mapping of tool ids to keys.


        Returns:
            None

        Postconditions:
            self._key_mappings will contain a dictionary of id -> key mappings
        """
        for tool_id in self._controller.image_tools.keys():
            tool = self._controller.image_tools[tool_id]
            self._key_mappings[tool_id] = tool.key_mapping

        for tool_id in self._key_mappings.keys():
            key = self._key_mappings[tool_id]

            self._reverse_key_mappings[key] = tool_id

    def _update_toolbar_state(self, tool_id):
        """
        Change the state of the buttons in the toolbar based on the button that
        has been chosen.

        Args:
            tool_id: The id of the tool that was chosen

        Returns:
            None

        Postconditions:
            The toolbar button matching the given id will be activated.
        """

        if not self._controller.image_tools[tool_id].persistant:
            return

        for id, button in self._toolbar_buttons.items():
            if id == tool_id and self._controller.image_tools[id].persistant:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])

    def _on_mousewheel(self, event):
        """
        Called when the mousewheel is scrolled.

        Args:
            event: The mouse event

        Returns:
            None
        """

        # On Linux, the events are different
        if event.num == 4:
            rotation = 120
        elif event.num == 5:
            rotation = -120

        # For Windows and Mac
        if event.delta != 0:
            rotation = event.delta

        # If control is down)
        if event.state - self._previous_state == 4:
            self._controller.adjust_tool(rotation)

    def _set_menubar_theme(self):
        """
        Set the theme for the menubar.


        Returns:
            None
        """

        background = self.style.lookup('MenuBar.TMenubutton', 'background')
        foreground = self.style.lookup('MenuBar.TMenubutton', 'foreground')

        activebackground = self.style.lookup('MenuBar.TMenubutton',
                                             'activebackground')
        activeforeground = self.style.lookup('MenuBar.TMenubutton',
                                             'activeforeground')

        self._menubar.config(background=background, foreground=foreground,
                             activebackground=activebackground,
                             activeforeground=activeforeground)

    def _set_filemenu_theme(self):

        background = self.style.lookup('Menu.TMenubutton', 'background')
        foreground = self.style.lookup('Menu.TMenubutton', 'foreground')

        activebackground = self.style.lookup('Menu.TMenubutton',
                                             'activebackground')
        activeforeground = self.style.lookup('Menu.TMenubutton',
                                             'activeforeground')

        self._filemenu.config(background=background, foreground=foreground,
                              activebackground=activebackground,
                              activeforeground=activeforeground)

    def _set_viewmenu_theme(self):

        background = self.style.lookup('Menu.TMenubutton', 'background')
        foreground = self.style.lookup('Menu.TMenubutton', 'foreground')

        activebackground = self.style.lookup('Menu.TMenubutton',
                                             'activebackground')
        activeforeground = self.style.lookup('Menu.TMenubutton',
                                             'activeforeground')

        self._viewmenu.config(background=background, foreground=foreground,
                              activebackground=activebackground,
                              activeforeground=activeforeground)

        self._previewmenu.config(background=background, foreground=foreground,
                                 activebackground=activebackground,
                                 activeforeground=activeforeground)

    def _set_helpmenu_theme(self):

        background = self.style.lookup('Menu.TMenubutton', 'background')
        foreground = self.style.lookup('Menu.TMenubutton', 'foreground')

        activebackground = self.style.lookup('Menu.TMenubutton',
                                             'activebackground')
        activeforeground = self.style.lookup('Menu.TMenubutton',
                                             'activeforeground')

        self._helpmenu.config(background=background, foreground=foreground,
                              activebackground=activebackground,
                              activeforeground=activeforeground)

    def _set_master_theme(self):
        background = self.style.lookup('Main.TFrame', 'background')
        self._master.config(background=background)


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
