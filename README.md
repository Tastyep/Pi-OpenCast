<div align="center">
  <img src="./assets/images/banner.png" alt="banner">
</div>
<h1 align="center" style="font-size: 50px; color:#000; font-weight: 600">OpenCast</h1>

OpenCast is a client-server media player that transforms your Raspberry Pi into an awesome streaming device.
All you need to make it work is a Raspberry Pi, an internet connection and a screen of your choice.

### Background
Opencast started off as a fork of the [RaspberryCast](https://github.com/vincelwt/RaspberryCast) project to implement features specific to my home setup. It has since evolved into a derivative work which includes a full rewrite of the server's code base allowing it to be maintainable and testable.

General goals of this project are:
- Using and supporting newer features of the python language standards.
- Conforming to the [PEP-8 guidelines](https://www.python.org/dev/peps/pep-0008/).
- Openness to contributions including pull requests with new features.
- Providing a continuous integration and unit tests to avoid regressions.
- Accommodating both the user and the developer with utilities to easily install/use/test the project.

### Features
Opencast supports streaming videos from the biggest platforms and a few [more sites](https://rg3.github.io/youtube-dl/supportedsites.html).

It is also possible to play medias located on your Raspberry Pi or from any device connected to it; to do so just provide the full path of the file.

Other features:
- Youtube playlist support.
- History and browsing support.
- Subtitle loading for local files (when name matches).
  - example: Tv Show S01E01.mp4, Tv Show S01E01.srt
- Dependency management using [Pipenv](https://github.com/pypa/pipenv)
- User friendly configuration file.

### How to
#### Install
- Clone this project and enter the Pi-Opencast directory.
- Execute the setup script and follow the instructions.

#### Use
First of all, note the <address> of your Raspberry-Pi by executing `sudo ifconfig`.

###### Computer
Open your favorite browser and go on `<address>:2020`


### License
OpenCast is distributed under the [MIT License](https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/LICENSE)
