import unicodedata, warnings

def width_of(char) -> int:
    width = unicodedata.east_asian_width(char)

    if width in ('F', 'W'):
        return 2
    elif width in ('H', 'N', 'Na'):
        return 1
    else:
        warnings.warn(f"The width of '{char}' is ambiguous.")
        return 1

print(width_of('a'))

def truncate_tabulate(data:list, widths:list) -> str:
    pass