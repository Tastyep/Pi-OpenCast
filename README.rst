.. image:: https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/assets/images/banner.png
   :scale: 80 %
   :align: center
   :alt: Banner

|

========
Opencast
========

.. image:: https://github.com/Tastyep/Pi-OpenCast/workflows/Test/badge.svg
   :target: https://github.com/Tastyep/Pi-OpenCast/actions?query=workflow%3ATest
   :alt: Test status for master branch

.. image:: https://codecov.io/gh/Tastyep/Pi-OpenCast/branch/develop/graph/badge.svg
   :target: https://codecov.io/gh/Tastyep/Pi-OpenCast
   :alt: codecov.io status for master branch

.. image:: https://github.com/Tastyep/Pi-OpenCast/workflows/Sanitize/badge.svg
   :target: https://github.com/Tastyep/Pi-OpenCast/actions?query=workflow%3ASanitize
   :alt: Sanitizing status for master branch

.. image:: https://github.com/Tastyep/Pi-OpenCast/workflows/Documentation/badge.svg
   :target: https://tastyep.github.io/Pi-OpenCast/
   :alt: OpenCast generated documentation

OpenCast is a streaming application whose goal is to transform a computer as small as a Raspberry Pi into
an awesome streaming device.

Key Features
============

 - Lightweight fast media server, able to run on raspberry-pi.
 - Tons of `supported sites <https://ytdl-org.github.io/youtube-dl/supportedsites.html>`_.
 - Stream support (Youtube, Twitch ...)
 - Playlist support
 - Local library.
 - VLC under the hood.

Background
===========

Opencast started off as a fork of `RaspberryCast <https://github.com/vincelwt/RaspberryCast>`_ to implement features specific to my home setup.
After some years this work has evolved into a testable and maintainable project named OpenCast.

General goals of the project are:

 - Using and supporting newer features of the python language standards.
 - Conforming to `PEP-8 guidelines <https://www.python.org/dev/peps/pep-0008/>`_.
 - Openness to contributions including pull requests with new features.
 - Providing a continuous integration and unit tests to avoid regressions.
 - Accommodating both the user and the developer with utilities to easily install/use/test the project.


System Dependencies
===================

 - Python 3.7+
 - nodejs
 - npm
 - curl
 - lsof
 - pip3

How To
======
Install
-------

.. code-block:: bash

   $ git clone https://github.com/Tastyep/Pi-OpenCast.git
   $ cd Pi-OpenCast && ./setup.sh

Use
---

- Note the address of the device running OpenCast by executing `sudo ifconfig`.
- Open your browser and go on `<address>:8081`

Source Code
===========

The project is hosted on `Github <https://github.com/Tastyep/Pi-OpenCast>`_.

Please feel free to file an issue on the `bug tracker <https://github.com/Tastyep/Pi-OpenCast/issues>`_
if you have found a bug or have some suggestion in order to improve OpenCast.

License
-------

OpenCast is distributed under the `MIT License <https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/LICENSE>`_.
