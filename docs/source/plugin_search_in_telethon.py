from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes


def tl_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    if options is None:
        options = {}

    set_classes(options)

    node = nodes.reference(
        rawtext,
        utils.unescape(text),
        refuri=f'https://docs.telethon.dev/en/latest/search.html?q={text}',
        **options,
    )

    return [node], []


def setup(app):
    app.add_role('telethon', tl_role)
