class TerminalVisualizer:
    """Format simulation output with terminal colors.

    Attributes:
        COLORS: ANSI escape codes indexed by color name.
        RESET: ANSI escape code that restores the default color.
    """

    COLORS: dict[str, str] = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
    }
    RESET: str = "\033[0m"

    def colorize(self, text: str, color: str | None) -> str:
        """Apply a supported color to text.

        Args:
            text: The text to color.
            color: Name of a color in ``COLORS``, or None.

        Returns:
            The text wrapped in ANSI color codes, or unchanged if the color
            is not supported.
        """
        code = self.COLORS.get(color or "", "")
        return f"{code}{text}{self.RESET}" if code else text
