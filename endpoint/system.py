import os
from flask import Blueprint
from io import StringIO
from lxml import etree
from pathlib import Path
from server import app
from server.message import Message
from util.config import config

system = Blueprint('system', app.name)


@system.route('/term', methods=['GET'])
def term():
    """
    Get terms and conditions
    """
    m = Message()

    # get directory of file
    parent = Path(__file__).parent.parent

    path = Path(str(parent) + os.sep + 'term.md')

    items = []

    # file reader
    with path.open() as reader:
        for row in reader:
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(row), parser=parser)

            for tag in tree.find('body').getchildren():
                name = tag.tag

                if name == 'br':
                    item = {'padding': '16.0'}

                    # append padding tag
                    items.append(item)
                elif name == 'h1':
                    item = {'title': tag.text}

                    # append title tag
                    items.append(item)
                elif name == 'h2':
                    item = {'subtitle': tag.text}

                    # append sub title tag
                    items.append(item)
                elif name == 'p':
                    item = {'text': tag.text}

                    # append text tag
                    items.append(item)
                elif name == 'li':
                    item = {'list': tag.text}

                    # append list tag
                    items.append(item)

    if len(items) == 0:
        m.message = 'The terms could not be loaded.'
        return m.json()

    m.items = items
    m.status = True

    return m.json()


@system.route('/version', methods=['GET'])
def version():
    """
    Get system version
    """
    m = Message(
        status=True,
        version=config.app.version,
    )

    return m.json()


@system.route('/ping', methods=['GET'])
def ping():
    """
    Return pong

    :rtype: str
    """
    return 'pong'
