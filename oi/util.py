# Utility functions that didn't fit anywhere else

import re


def split(text):
    """ Split text into arguments accounting for muti-word arguments
    which are double quoted """

    # Cleanup text
    text = text.strip()
    text = re.sub('\s+', ' ', text)  # collpse multiple spaces

    space, quote, parts = ' ', '"', []
    part, quoted = '', False

    for char in text:

        # Encoutered beginning double quote
        if char is quote and quoted is False:
            quoted = True
            continue

        # Encountered the ending double quote
        if char is quote and quoted is True:
            quoted = False
            parts.append(part.strip())
            part = ''
            continue

        # Found space in quoted
        if char is space and quoted is True:
            part += char
            continue

        # Found space but not quoted
        if char is space:
            if part:
                parts.append(part)
                part = ''
            continue

        # Found other character
        if char is not space:
            part += char
            continue

    if part:
        parts.append(part.strip())

    return parts
