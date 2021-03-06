# Paperwork installation on GNU/Linux Fedora


## Package

Currently, there is no official Fedora package for Paperwork.

Note that Paperwork depends on [Pillow](https://pypi.python.org/pypi/Pillow/).
Pillow may conflict with the package python-imaging (aka PIL).


## Build dependencies

    $ sudo dnf install python-pip python-setuptools python-devel

    # Pillow build dependencies :
    $ sudo dnf install libjpeg-turbo-devel zlib-devel

    # PyEnchant dependency
    $ sudo dnf install enchant-devel

Note that `yum` is deprecated since Fedora 22 and replaced by `dnf`. If
you use an older Fedora, replace instances of `dnf` above by `yum`. The
rest of the commands are the same.

## System-wide installation

    $ sudo pip install paperwork
    # This command will install Paperwork and tell you if some extra
    # dependencies are required.
    # IMPORTANT: the extra dependencies list may be drown in the output. You
    # may miss it.

Some dependencies cannot be installed automatically. You can find all the
missing dependencies by running 'paperwork-chkdeps'.

    $ paperwork-chkdeps


## Running Paperwork

A shortcut should be available in the menus of your window manager (you may
have to log out first).

You can also start Paperwork by running the command 'paperwork'.

Enjoy :-)
