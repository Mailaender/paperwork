#!/usr/bin/env python
#    Paperwork - Using OCR to grep dead trees the easy way
#    Copyright (C) 2014  Jerome Flesch
#
#    Paperwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Paperwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Paperwork.  If not, see <http://www.gnu.org/licenses/>.

import glob
import logging
import os
import sys

import heapq
import gettext
from gi.repository import Gdk
from gi.repository import Gtk

import PIL.Image


_ = gettext.gettext
logger = logging.getLogger(__name__)

PREFIX = os.environ.get('VIRTUAL_ENV', '/usr')

UI_FILES_DIRS = []
if getattr(sys, 'frozen', False):
    UI_FILES_DIRS += [os.path.join(sys._MEIPASS, "data")]
UI_FILES_DIRS += [
    ".",
    "src/paperwork/frontend",
    "data",
    PREFIX + "/local/share/paperwork",
    PREFIX + "/share/paperwork",

    # XXX(Jflesch): The following locations are unexpected
    # but it seems those are the locations used by Pip
    # (sys.prefix in setup.py ?)
    PREFIX + "/local/lib/python*/dist-packages/usr/share/paperwork",
    PREFIX + "/local/lib/python*/dist-packages/usr/local/share/paperwork",
    PREFIX + "/lib/python*/dist-packages/usr/share/paperwork",
    PREFIX + "/lib/python*/dist-packages/usr/local/share/paperwork",
]


def load_uifile(filename):
    """
    Load a .glade file and return the corresponding widget tree

    Arguments:
        filename -- glade filename to load.
            This function will (try to) figure out from where it must be loaded.

    Returns:
        GTK Widget tree

    Throws:
        Exception -- If the file cannot be found
    """
    widget_tree = Gtk.Builder()
    has_ui_file = False
    for ui_glob_dir in UI_FILES_DIRS:
        for ui_dir in glob.glob(ui_glob_dir):
            ui_file = os.path.join(ui_dir, filename)
            if os.access(ui_file, os.R_OK):
                logger.info("UI file used: " + ui_file)
                widget_tree.add_from_file(ui_file)
                has_ui_file = True
                break
        if has_ui_file:
            break
    if not has_ui_file:
        logger.error("Can't find resource file '%s'. Aborting" % filename)
        raise Exception("Can't find resource file '%s'. Aborting" % filename)
    return widget_tree


def load_cssfile(filename):
    """
    Load a .css file

    Arguments:
        filename -- css filename to load.
            This function will (try to) figure out from where it must be loaded.

    Throws:
        Exception -- If the file cannot be found
    """
    css_provider = Gtk.CssProvider()
    has_css_file = False
    for css_glob_dir in UI_FILES_DIRS:
        for css_dir in glob.glob(css_glob_dir):
            css_file = os.path.join(css_dir, filename)
            if os.access(css_file, os.R_OK):
                logger.info("CSS file used: " + css_file)
                css_provider.load_from_path(css_file)
                has_css_file = True
                break
        if has_css_file:
            break
    if not has_css_file:
        logger.error("Can't find resource file '%s'. Aborting" % filename)
        raise Exception("Can't find resource file '%s'. Aborting" % filename)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


_SIZEOF_FMT_STRINGS = [
    _('%3.1f bytes'),
    _('%3.1f KB'),
    _('%3.1f MB'),
    _('%3.1f GB'),
    _('%3.1f TB'),
]


def load_image(filename):
    """
    Load an image from Paperwork data
    """
    for img_directory in UI_FILES_DIRS:
        for img_dir in glob.glob(img_directory):
            img = os.path.join(img_dir, filename)
            if os.path.exists(img):
                return PIL.Image.open(img)
    raise Exception("Can't find image '{}' !".format(filename))


def sizeof_fmt(num):
    """
    Format a number of bytes in a human readable way
    """
    for string in _SIZEOF_FMT_STRINGS:
        if num < 1024.0:
            return string % (num)
        num /= 1024.0
    return _SIZEOF_FMT_STRINGS[-1] % (num)


class PriorityQueueIter(object):

    def __init__(self, queue):
        """
        Arguments:
            queue --- must actually be an heapq
        """
        self.queue = queue[:]

    def next(self):
        try:
            return heapq.heappop(self.queue)[2]
        except IndexError:
            raise StopIteration()

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self


class PriorityQueue(object):

    def __init__(self):
        self.__last_idx = 0
        self.elements = []

    def purge(self):
        self.elements = []

    def add(self, priority, element):
        """
        Elements with a higher priority are returned first
        """
        heapq.heappush(
            self.elements,
            (-1 * priority, self.__last_idx, element)
        )
        self.__last_idx += 1

    def remove(self, target):
        to_remove = None
        for element in self.elements:
            if element[2] == target:
                to_remove = element
                break
        if to_remove is None:
            raise ValueError()
        self.elements.remove(to_remove)
        heapq.heapify(self.elements)

    def __iter__(self):
        return PriorityQueueIter(self.elements)

    def __str__(self):
        return "PW[%s]" % (", ".join([str(x) for x in self.elements]))


def connect_actions(actions):
    for action in actions:
        for button in actions[action][0]:
            if button is None:
                logger.error("MISSING BUTTON: %s" % (action))
        try:
            actions[action][1].connect(actions[action][0])
        except:
            logger.error("Failed to connect action '%s'" % action)
            raise
