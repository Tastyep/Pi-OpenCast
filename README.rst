.. image:: https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/assets/images/banner.webp
   :scale: 80 %
   :align: center
   :alt: Banner

|

========
OpenCast
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

OpenCast is a home theater application whose goal is to transform a computer as small as a Raspberry Pi into
an awesome streaming device.

Key Features
============

 - Lightweight fast media server, able to run on raspberry-pi.
 - Tons of `supported sites <https://ytdl-org.github.io/youtube-dl/supportedsites.html>`_.
 - Stream support (Youtube, Twitch ...)
 - Playlist support
 - Local library.
 - VLC under the hood.

How To
======
Install
-------

.. code-block:: bash

   $ git clone https://github.com/Tastyep/Pi-OpenCast.git
   $ cd Pi-OpenCast && ./setup.sh

⚠️ Because the web application has grown in size over time, it is possible that building on a raspberry-pi with <= 1giga of RAM will fail as it will run out of memory. In that case, you will have to build it manually on your computer by running the following command:

.. code-block:: bash

   $ ./OpenCast.sh build webapp

Then transfer the generated ``./webapp/build`` directory into the ``webapp`` directory on your raspberry-pi (filezilla is your friend).


Use
-------

After successfully installing OpenCast, you should note the IP address of your raspberry-pi:


.. code-block:: bash

   $ hostname -I

You can then access the webpage from any device on the same local network at ``<ip-addr>:8081``

Monitor
-------

OpenCast is managed as a systemd service and loaded automatically at startup time.
To interact with the service, two options are available:

- Using systemctl (**recommended**)

.. code-block:: bash

   $ systemctl --user [start|stop|restart|status] opencast

- Using the shell entry-point (**advanced**):

.. code-block:: bash

   $ ./OpenCast.sh service [start|stop|restart|status]

Logs can be accessed running:

.. code-block:: bash

   $ journalctl --user -u opencast
   $ ./OpenCast.sh service back log

Configure
-------

The backend and the web application can be configured through their configuration file:

- Backend: ``config.yml``
- Webapp: ``webapp/.env``

Source Code
===========

The project is hosted on `Github <https://github.com/Tastyep/Pi-OpenCast>`_.

Please feel free to file an issue on the `bug tracker <https://github.com/Tastyep/Pi-OpenCast/issues>`_
if you have found a bug or have suggestions to improve OpenCast.

License
-------

OpenCast is distributed under the `MIT License <https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/LICENSE>`_.
