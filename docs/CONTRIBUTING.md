# Contributing to Nimbus

Thanks for helping improve Nimbus Weather CLI. This guide walks through setting up the project, making a change, checking it, and opening a pull request.

## What you need

- Git
- Python 3.11 or newer
- Internet access to try live weather lookups (the test suite does not require live API data)

## Get the project

If you do not have write access to the Nimbus repository, first create a fork on GitHub. Then clone your fork:

```sh
git clone https://github.com/<your-github-name>/nimbus.git
cd nimbus
```

If you do have write access, you can clone `https://github.com/olympus-mons26/nimbus.git` instead.

Create a branch for your change:

```sh
git switch -c describe-your-change
```

## Set up Python

Create a virtual environment and install Nimbus with its test dependencies.

### macOS and Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

If PowerShell does not allow environment activation, you can run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

## Run Nimbus

With the virtual environment active, try the command-line app:

```sh
wf London
wf Tokyo -h -f
```

To see all supported commands and options, run `wh` or `wf --help`.

## Make and check your change

- Keep changes focused and follow the existing code style.
- Add or update tests when changing behavior. Avoid tests that depend on live weather services or include private location data.
- Keep error messages actionable. Do not commit credentials, tokens, or other secrets.
- Preserve Open-Meteo attribution and follow its applicable usage terms when changing API behavior.

Run the test suite before opening a pull request:

```sh
python -m pytest -v
```

The project does not currently require a separate formatter or linter. If you update user-facing behavior or command options, update the README as well.

## Open a pull request

Review the changed files, commit your work, and push your branch:

```sh
git status
git add <files-you-changed>
git commit -m "Describe your change"
git push -u origin describe-your-change
```

Replace `<files-you-changed>` with the paths you edited, such as `README.md` or `src/nimbus/main.py`.

On GitHub, open a pull request from your branch to `olympus-mons26/nimbus`'s `main` branch. In the description, explain what changed, why it is useful, and which tests you ran. Include screenshots or sample terminal output when they help explain a visible change.

## More guides

- For building a standalone executable locally, see the [README build instructions](../README.md#build-a-standalone-executable).
- Homebrew release publishing is a maintainer task requiring repository secrets. See the [Homebrew publishing guide](./HOMEBREW.md) if you maintain the release workflow.
