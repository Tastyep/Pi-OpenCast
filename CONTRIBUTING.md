# Contributing

## Instructions for contributors

Thank you for considering contributing to OpenCast!

In order to make a clone of the GitHub repo: open the link and press the
"Fork" button on the upper-right menu of the web page.

I hope everybody knows how to work with git and github nowadays :)

#### Setup and workflow

The workflow is pretty straightforward:

- Clone the main repository locally.

```
    $ git clone https://github.com/Tastyep/Pi-OpenCast
    $ cd Pi-OpenCast
```

- Setup your machine with the dev environment.

```
    $ ./setup.sh
```

- Add your fork as a remote to push your work to.
  Replace `{username}` with your username. This names the remote "fork", the default OpenCast remote is "origin".

```
    $ git remote add fork https://github.com/{username}/Pi-OpenCast
```

- Branch from develop

```
    $ git fetch origin
    $ git checkout -b your-branch-name origin/develop
```

- Make your changes, write [good commit messages](https://github.com/erlang/otp/wiki/writing-good-commit-messages).
- Include tests and check for regressions.

```
    $ ./OpenCast.sh test back
```

- Check for format and linter errors.

```
    $ ./OpenCast.sh lint all
    $ ./OpenCast.sh format all
```

- Push your commits to your fork on GitHub and open a pull request.

```
    $ git push --set-upstream fork your-branch-name
```

#### Building the docs

```
    $ ./OpenCast.sh generate doc
```

Open `build/html/index.html` in your browser to view the docs.

Read more about [Sphinx](https://www.sphinx-doc.org/en/stable/).
