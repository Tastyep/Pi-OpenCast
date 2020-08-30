<div align="center">
  <img src="./assets/images/banner.png" alt="banner">
</div>
<h1 align="center" style="font-size: 50px; color:#000; font-weight: 600">OpenCast</h1>

![Test](https://github.com/Tastyep/Pi-OpenCast/workflows/Test/badge.svg)
[![codecov](https://codecov.io/gh/Tastyep/Pi-OpenCast/branch/develop/graph/badge.svg)](https://codecov.io/gh/Tastyep/Pi-OpenCast)
![Sanitize](https://github.com/Tastyep/Pi-OpenCast/workflows/Sanitize/badge.svg)
[![Documentation](https://github.com/Tastyep/Pi-OpenCast/workflows/Documentation/badge.svg)](https://tastyep.github.io/Pi-OpenCast/)

OpenCast is a streaming application whose goal is to transform a computer as small as a Raspberry Pi into an awesome streaming device.

### Key Features

- Lightweight and Fast, runs on Raspberry Pi.
- Many [supported sites](https://rg3.github.io/youtube-dl/supportedsites.html).
- Reworked interface.
- Youtube playlist support.
- Subtitle support for both local and remote videos.

### Background

Opencast started off as a fork of [RaspberryCast](https://github.com/vincelwt/RaspberryCast) to implement features specific to my home setup. After some years this work has evolved into a testable and maintainable project named OpenCast.

General goals of the project are:

- Using and supporting newer features of the python language standards.
- Conforming to [PEP-8 guidelines](https://www.python.org/dev/peps/pep-0008/).
- Openness to contributions including pull requests with new features.
- Providing a continuous integration and unit tests to avoid regressions.
- Accommodating both the user and the developer with utilities to easily install/use/test the project.

### How to

#### Install

```
$ git clone https://github.com/Tastyep/Pi-OpenCast.git
$ cd Pi-OpenCast && ./setup.sh
```

#### Use

- Note the address of the device running OpenCast by executing `sudo ifconfig`.
- Open your browser and go on `<address>:8081`

### License

OpenCast is distributed under the [MIT License](https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/LICENSE)
