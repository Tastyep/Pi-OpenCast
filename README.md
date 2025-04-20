<p align="center">
  <img src="https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/assets/images/banner.webp" alt="Banner" width="80%">
</p>

---

# OpenCast

[![Test](https://github.com/Tastyep/Pi-OpenCast/workflows/Test/badge.svg)](https://github.com/Tastyep/Pi-OpenCast/actions?query=workflow%3ATest)
[![Codecov](https://codecov.io/gh/Tastyep/Pi-OpenCast/branch/develop/graph/badge.svg)](https://codecov.io/gh/Tastyep/Pi-OpenCast)
[![Sanitize](https://github.com/Tastyep/Pi-OpenCast/workflows/Sanitize/badge.svg)](https://github.com/Tastyep/Pi-OpenCast/actions?query=workflow%3ASanitize)
[![Docs](https://github.com/Tastyep/Pi-OpenCast/workflows/Documentation/badge.svg)](https://tastyep.github.io/Pi-OpenCast/)

OpenCast is a home theater application designed to transform a computer as small as a Raspberry Pi into an awesome streaming device.

## 🚀 Key Features

- ⚡ Lightweight fast media server, able to run on raspberry-pi.
- 🌐 Tons of [supported sites](https://ytdl-org.github.io/youtube-dl/supportedsites.html).
- 📺 Stream support (YouTube, Twitch, etc.)
- 🎵 Playlist support
- 📁 Local media library
- 🧠 VLC under the hood

## 📦 How To

### 🔧 Install

```bash
git clone https://github.com/Tastyep/Pi-OpenCast.git
cd Pi-OpenCast && ./setup.sh
```

> ⚠️ **Note:** On Raspberry Pi devices with ≤ 1 GB RAM, build may fail due to memory limitations. In that case, build on a more powerful computer using:

```bash
./OpenCast.sh build webapp
```

Then, transfer the generated `./webapp/build` directory into the `webapp` directory on your Raspberry Pi (FileZilla is your friend).

### 🌍 Use

Get your Pi’s IP address:

```bash
hostname -I
```

Then access the web UI from a device on the same local network:

```
http://<ip-addr>:8081
```

### 🛠️ Monitor

OpenCast runs as a systemd service and starts automatically.

#### Using `systemctl` (recommended):

```bash
systemctl --user [start|stop|restart|status] opencast
```

#### Using the shell entry-point (advanced):

```bash
./OpenCast.sh service [start|stop|restart|status]
```

#### Viewing logs:

```bash
journalctl --user -u opencast
./OpenCast.sh service back log
```

### ⚙️ Configure

- Backend config: `config.yml`
- Webapp config: `webapp/.env`

## 🧾 Source Code

The project is hosted on [GitHub](https://github.com/Tastyep/Pi-OpenCast).

Found a bug or have an improvement idea?  
Feel free to [file an issue](https://github.com/Tastyep/Pi-OpenCast/issues)!

## 📄 License

Distributed under the [MIT License](https://raw.githubusercontent.com/Tastyep/Pi-OpenCast/master/LICENSE).
