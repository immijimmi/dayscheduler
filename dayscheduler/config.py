from .constants import Constants


class Config:
    TIMELINE_LIMITS = (5, 24)  # Start hour, end hour (non-inclusive)

    # Styles below are applied to the relevant components/widgets in the same order they are presented in
    THEME = {
        "timeline": {
            "frame": {
                "bg": Constants.COLOURS["very_light_grey"],
                "relief": "sunken",
                "borderwidth": Constants.BORDERWIDTH_TINY
            },
            "cell_frame": {
                "relief": "ridge",
                "borderwidth": Constants.BORDERWIDTH_TINY
            },
            "margin_frame": {
                "relief": "ridge",
                "borderwidth": Constants.BORDERWIDTH_MEDIUM
            },
            "margin_label": {
                "fg": Constants.COLOURS["very_dark_grey"],
                "font": Constants.FONT_SMALL
            },
            "entry_frame": {
                "relief": "raised",
                "borderwidth": Constants.BORDERWIDTH_SMALL
            },
            "entry_label": {
                "fg": Constants.COLOURS["very_light_green"]
            },
            "entry_label_period": {
                "font": Constants.FONT_TINY
            },
            "entry_label_title": {
                "font": Constants.FONT_LARGE_BOLD,
                "padx": Constants.PAD_SMALL,
                "pady": Constants.PAD_SMALL
            },
            "entry_label_title_compact": {
                "font": Constants.FONT_TINY_BOLD
            },
            "even_non_pending": {
                "bg": Constants.COLOURS["grey"]
            },
            "even_pending": {
                "bg": Constants.COLOURS["light_grey"]
            },
            "odd_non_pending": {
                "bg": Constants.COLOURS["very_light_grey"]
            },
            "odd_pending": {
                "bg": Constants.COLOURS["very_very_light_grey"]
            },
            "entry_non_pending": {
                "bg": Constants.COLOURS["green"]
            },
            "entry_pending": {
                "bg": Constants.COLOURS["light_green"]
            }
        },
        "workspace": {
            "frame": {
                "bg": Constants.COLOURS["very_light_grey"],
                "relief": "groove",
                "borderwidth": Constants.BORDERWIDTH_SMALL
            },
            "entry_frame": {
                "relief": "raised",
                "borderwidth": Constants.BORDERWIDTH_SMALL,
                "padx": Constants.PAD_MEDIUM,
                "pady": Constants.PAD_MEDIUM
            },
            "bin_frame": {
                "relief": "sunken",
                "borderwidth": Constants.BORDERWIDTH_SMALL
            },
            "string_editor": {
                "bg": Constants.COLOURS["very_light_green"],
                "fg": Constants.COLOURS["green"],
                "font": Constants.FONT_LARGE_BOLD
            },
            "stepper": {
                "bg": Constants.COLOURS["light_green"],
                "font": Constants.FONT_SMALL
            },
            "stepper_button": {
                "borderwidth": Constants.BORDERWIDTH_TINY,
                "fg": Constants.COLOURS["dark_green"],
                "disabledforeground": Constants.COLOURS["green"]
            },
            "stepper_label": {
                "relief": "raised",
                "borderwidth": Constants.BORDERWIDTH_TINY,
                "fg": Constants.COLOURS["dark_green"]
            },
            "non_pending": {
                "bg": Constants.COLOURS["very_light_grey"]
            },
            "pending": {
                "bg": Constants.COLOURS["very_very_light_grey"]
            },
            "entry_non_pending": {
                "bg": Constants.COLOURS["green"]
            },
            "entry_pending": {
                "bg": Constants.COLOURS["light_green"]
            },
            "bin_non_pending": {
                "bg": Constants.COLOURS["light_yellow"]
            },
            "bin_pending": {
                "bg": Constants.COLOURS["yellow"]
            }
        }
    }
