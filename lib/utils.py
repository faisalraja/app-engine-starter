from jinja2._markupsafe import Markup


def nl2br(value):
    if value:
        return Markup(value.replace('\n', '<br>\n'))
    return value


def pluralize(word, **kwargs):
    count = kwargs.get('count', None)
    plural_suffix = kwargs.get('plural_suffix', 's')
    singular_suffix = kwargs.get('singular_suffix', None)

    if count is not None:
        word = [count, word]
    elif not isinstance(word, list):
        word = word.split(' ')
    try:
        if int(word[0]) != 1:
            word[1] += plural_suffix
        elif singular_suffix:
            word[1] += singular_suffix
    except ValueError:  # Invalid string that's not a number.
        pass
    if count is not None:
        return word.pop()
    return ' '.join(word)