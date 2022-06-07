"""
File Name: light_theme.py

Authors: Kyle Seidenthal

Date: 22-05-2020

Description: Light Theme

"""

from tkinter import ttk

colours = {
            "toolbar_activate": "#ffde4d",
            "pbar_colour": "#2640b5",
            "link_colour": "#5978ff",
            "bg_level_0": "#d9d9d9",
            "fg_level_0": "#000000",
            "bg_level_1": "#c4c4c4",
            "fg_level_1": "#000000",
            "bg_level_2": "#a8a8a8",
            "fg_level_2": "#000000",
            "bg_level_3": "#919191",
            "fg_level_3": "#000000"

        }


settings = {
        "PersistantToolbar.TButton": {
            "configure": {
                    "background": colours['bg_level_2'],
                    "foreground": colours['fg_level_2'],
                    "borderwidth": 2,
                    "bordercolor": colours['bg_level_2']
                },
            "map": {
                "background": [('pressed', colours['toolbar_activate']),
                               ('disabled', colours['toolbar_activate']),
                               ('active', colours['bg_level_3'])],
                "foreground": [],
                "relief": [('pressed', 'sunken'), ('disabled', 'sunken'),
                           ('!disabled', 'flat')]
                }

            },
        "Toolbar.TButton": {
            "configure": {
                "background": colours['bg_level_2'],
                "foreground": colours['fg_level_2']
                },
            "map": {
                "background": [('active', colours['bg_level_3'])],
                "relief": [('pressed', 'sunken')]
                }
            },
        "Toolbar.TFrame": {
            "configure": {
                "borderwidth": 1,
                "bordercolor": colours['bg_level_2'],
                "background": colours['bg_level_1'],
                "foreground": colours['fg_level_1']
                }

            },
        "Toolbar.TLabel": {
            "configure": {
                "background": colours['bg_level_1'],
                "foreground": colours['fg_level_1']
                }
            },
        "TSeparator": {
            "configure": {
                "background": colours['bg_level_0'],
                "foreground": colours['fg_level_0']
                }
            },
        "MenuBar.TMenubutton": {
            "configure": {
                "background": colours['bg_level_1'],
                "foreground": colours['fg_level_1'],
                "bordercolor": colours['bg_level_2'],
                "activeforeground": colours['fg_level_2'],
                "activebackground": colours['bg_level_2']
                }
            },
        "Menu.TMenubutton": {
                "configure": {
                    "background": colours['bg_level_2'],
                    "foreground": colours['fg_level_2'],
                    "bordercolor": colours['bg_level_3'],
                    "activeforeground": colours['fg_level_3'],
                    "activebackground": colours['bg_level_3']
                    }
                },
        "TFrame": {
                "configure": {
                    "background": colours['bg_level_1']
                    }
                },
        "Main.TFrame": {
                "configure": {
                    "background": colours['bg_level_0']
                    }
                },
        "TEntry": {
                "configure": {
                    "background": colours['bg_level_3'],
                    "foreground": colours['fg_level_3']
                    }
                },
        "InfoPanel.TLabel": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1'],
                    "padding": 10
                    }
                },
        "InfoPanel.TFrame": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1'],
                    "bordercolor": colours['bg_level_2'],
                    }
                },
        "Horizontal.TProgressbar": {
                "configure": {
                    "background": colours['pbar_colour'],
                    "foreground": colours['pbar_colour'],
                    "troughcolor": colours['fg_level_2']
                    }
            },
        "InfoPanel.Horizontal.TScale": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1'],
                    "troughcolor": colours['bg_level_3']
                    }
                },
        "Horizontal.TScrollbar": {
                "configure": {
                    "background": colours['bg_level_3'],
                    "foreground": colours['fg_level_3'],
                    "highlightcolor": colours['fg_level_3'],
                    "troughcolor": colours['bg_level_2'],
                    "bordercolor": colours['bg_level_2']
                    }
                },
        "Vertical.TScrollbar": {
                "configure": {
                    "background": colours['bg_level_3'],
                    "foreground": colours['fg_level_3'],
                    "highlightcolor": colours['fg_level_3'],
                    "troughcolor": colours['bg_level_2'],
                    "bordercolor": colours['bg_level_2']
                    }
                },
        "HelpDialog.TLabel": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1']
                    }
                },
        "Link.TLabel": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['link_colour']
                    }
                },
        "HelpDialog.TFrame": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1']
                    }
                },
        "KeyboardGroup.TFrame": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['bg_level_2'],
                    "padding": 10
                    }
                },
        "TButton": {
                "configure": {
                    "background": colours['bg_level_2'],
                    "foreground": colours['fg_level_2']
                    },
                "map": {
                    "background": [('active', colours['bg_level_3'])],
                    "relief": [('pressed', 'sunken')]
                    }
                },
        "TLabel": {
            "configure": {
                "background": colours['bg_level_1'],
                "foreground": colours['fg_level_1']
                }
            },
        "TMenuButton": {
                "configure": {
                    "background": colours['bg_level_2'],
                    "foreground": colours['bg_level_2']
                    }
                },
        "TPanedWindow": {
                "configure": {
                    "background": colours['bg_level_3'],
                    "foreground": colours['fg_level_3']
                    }
                },
        "Canvas.TFrame": {
                "configure": {
                    "background": colours['bg_level_0'],
                    "foreground": colours['fg_level_0']
                    }
                },
        "ButtonPanel.TFrame": {
                "configure": {
                    "background": colours['bg_level_1'],
                    "foreground": colours['fg_level_1']
                    }
                },
        "Preview.TFrame": {
                "configure": {
                    "borderwidth": 3,
                    "relief": "groove"
                }
            }

}

style = ttk.Style()

style.theme_create("light_theme", "clam", settings=settings)
