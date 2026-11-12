# Setup on Windows

One-time setup to run the pipeline and contribute from a Windows machine. All commands are for **PowerShell**.

## 1. Install Python 3.12 and Git

```powershell
winget install Python.Python.3.12
winget install Git.Git
```

Close and reopen PowerShell, then check:

```powershell
py -3.12 --version
git --version
```

## 2. Set your Git identity

Commits carry a name and an email address, and both are public in a public repository. To keep your real address private, use the no-reply address GitHub gives you: on GitHub go to **Settings → Emails**, tick **Keep my email addresses private**, and copy the address ending in `@users.noreply.github.com`.

```powershell
git config --global user.name "Your Name or Username"
git config --global user.email "ID+username@users.noreply.github.com"
```

## 3. Clone the repository

```powershell
git clone https://github.com/CMkc34/Ino_Mgmt.git
cd Ino_Mgmt
```

## 4. Create a virtual environment and install the dependencies

A virtual environment keeps this project's Python packages separate from everything else on the machine.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell refuses to run the activation script, allow local scripts for your user once, then try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Activate the environment (`.venv\Scripts\Activate.ps1`) every time you open a new PowerShell window for this project. The prompt shows `(.venv)` when it is active.

## 5. Check that everything works

```powershell
python -m pytest
python -m pipelines run all
```

Expected: all tests pass, and the pipeline prints one status line per step. Steps without data yet report `skipped`.

## 6. Make a change the project way

```powershell
git switch -c my-first-change      # new branch
# ...edit a file...
git add .
git commit -m "Describe what changed and why"
git push -u origin my-first-change
```

Then open a pull request on GitHub, wait for the checks to turn green, and merge.

## 7. Fetch data from the source

A normal pipeline run reads the stored snapshot and needs no network. Fetching a new snapshot does:

```powershell
python -m pipelines run trends --refresh
```

This writes two files into `data\raw\`: the counts (`publication_counts_<date>.csv`) and a note with the source, date and queries (`.meta.json`). Commit both.

To judge a search query by hand, list 20 random works it finds:

```powershell
python -m pipelines sample digital_twins
```

If the source asks for an API key, set it for the current PowerShell window only. It is then read from the environment and never stored in a file:

```powershell
$env:OPENALEX_API_KEY = "paste-your-key-here"
$env:OPENALEX_MAILTO  = "your-contact-address"   # optional courtesy to the source
```

Never write a key into `config.yaml`, the code or a commit.

## Troubleshooting

| Problem | Fix |
|---|---|
| `py` is not recognised | Reopen PowerShell after installing Python, or reinstall with "Add python.exe to PATH" ticked. |
| `python` opens the Microsoft Store | Activate the virtual environment first (step 4). |
| `git push` asks for a password | Sign in through the browser window that Git for Windows opens. |
| `git status` shows changes after a pipeline run | Report it as a bug: outputs are meant to be identical on every run. |
| `error: OpenAlex refused the request` | The source wants an API key. See step 7. |
| `error: OpenAlex rejected the request (HTTP 400)` | A search query in `config.yaml` is malformed. The message shows the source's explanation. |
