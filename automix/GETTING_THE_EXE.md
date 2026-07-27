# Getting AutoMix.exe without installing Python locally

`INSTALL.bat` needs Python on your machine because it builds the `.exe`
right there. If you'd rather skip installing anything and just get a
finished `AutoMix.exe`, GitHub can build it for you for free, on their
own Windows machine — you never touch Python.

## One-time setup (about 5 minutes)

1. Create a free account at https://github.com/join if you don't have one.
2. Create a new repository (https://github.com/new) — any name, e.g.
   `automix`. Public or private both work.
3. Upload this whole `automix` folder into that repository. Easiest way:
   on the repo page, click **"uploading an existing file"** and drag the
   contents in (or use `git push` if you're comfortable with git).
4. Go to the **Actions** tab on your repo. You should see a workflow
   called **"Build AutoMix.exe (Windows)"** run automatically (it's
   already included at `.github/workflows/build-windows.yml`). If it
   doesn't start on its own, click it and press **"Run workflow."**
5. Wait 3-5 minutes for it to finish (green checkmark).
6. Click the finished run → scroll to **Artifacts** → download
   **AutoMix-windows**. Unzip it — that's your real, finished
   `AutoMix.exe`, built the same way any commercial Windows app is
   built.

## After that

That `AutoMix.exe` runs on any Windows machine with no Python, no
install step, nothing else needed — copy it anywhere, double-click it.
This is genuinely the same kind of file as the plugins/standalones
you've installed before; the only reason it wasn't handed to you that
way from the start is that building it requires a Windows machine, and
I only have a Linux one.

If you update any `.py` file later and push the change to the same
repo, GitHub will automatically rebuild `AutoMix.exe` for you again.
