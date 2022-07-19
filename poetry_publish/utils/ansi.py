import re


def strip_style(output: str) -> str:
    """
    Strip ANSI style sequences from a string.
    """
    ESC = '\x1b'
    ANSI_STYLE_RE = re.compile(fr'{ESC}\[[^m]*m')
    return ANSI_STYLE_RE.sub('', output)
