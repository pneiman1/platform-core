# platform-core — Setup from scratch

This guide takes a **fresh machine** to a working platform-core development
environment with a verified Snowflake connection. platform-core is the shared
library every vertical (DermIQ, etc.) installs in editable mode, so set it up
**first**, then the vertical repo (see `dermiq/docs/SETUP.md`).

**Supported platforms:** macOS (Intel & Apple Silicon), Linux, and Windows via
WSL2. Steps are identical across platforms except where a callout marks them
**macOS** vs **Linux / WSL2**.

> WSL2 note: run everything inside your WSL2 Linux distribution (Ubuntu), not
> PowerShell. The Linux / WSL2 commands below apply.

---

## 1. Install the toolchain

You need: **Python 3.12**, **git**, **AWS CLI**, the **Astronomer CLI** (`astro`,
for Airflow later), and **Docker Desktop**.

### Python 3.12

**macOS**
```bash
brew install python@3.12
python3.12 --version
```
> Homebrew's Python can shadow the system Python — always invoke `python3.12`
> explicitly (or use `pyenv`). See [MACOS-NOTES](../../dermiq/docs/MACOS-NOTES.md)
> in the dermiq repo for the conflict details.

**Linux / WSL2**
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
python3.12 --version
```

### git, AWS CLI, Astronomer CLI

**macOS** (Homebrew formula names differ from apt — note `awscli`, not `aws-cli`):
```bash
brew install git awscli
brew install astro          # Astronomer CLI
```

**Linux / WSL2**
```bash
sudo apt install -y git
sudo apt install -y awscli                     # or the official bundle installer
curl -sSL https://install.astronomer.io | sudo bash -s   # Astronomer CLI
```

### Docker Desktop

- **macOS:** download Docker Desktop from docker.com and install the `.dmg`.
  On Apple Silicon it runs natively (arm64).
- **Linux / WSL2:** install Docker Desktop for Windows and enable **Settings →
  Resources → WSL Integration** for your distro. (Docker Engine in-distro works
  too.) Verify with `docker run hello-world`.

---

## 2. Configure git identity + SSH (identical on every platform)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Create an SSH key if you don't have one, then add the public key to GitHub.
ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub        # paste into GitHub → Settings → SSH keys
ssh -T git@github.com            # should greet you by username
```

---

## 3. Clone platform-core and create a virtualenv

Clone both repos as **siblings** under `~/projects` (the vertical's editable
install relies on the relative path `../platform-core`):

```
~/projects/
├── platform-core/      ← this repo
└── dermiq/             ← set up next, see dermiq/docs/SETUP.md
```

```bash
mkdir -p ~/projects && cd ~/projects
git clone git@github.com:pneiman1/platform-core.git
cd platform-core

python3.12 -m venv .venv
source .venv/bin/activate        # macOS & Linux/WSL2 (bash/zsh)
```

## 4. Install the library

```bash
pip install --upgrade pip
pip install -e ".[all]"          # library + all optional toolchains
```

## 5. Configure Snowflake credentials

```bash
cp .env.example .env
```

**Auth is key-pair (JWT), not password.** Snowflake enforces MFA, which password
auth can't satisfy headless, so the connection helper uses key-pair auth by default
(password is a legacy fallback for non-MFA accounts). Generate a key-pair once and
register the public key on your user:

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -outform PEM \
  -out ~/.ssh/snowflake_rsa_key.p8 -passout pass:<passphrase>
openssl rsa -in ~/.ssh/snowflake_rsa_key.p8 -passin pass:<passphrase> \
  -pubout -out ~/.ssh/snowflake_rsa_key.pub
chmod 600 ~/.ssh/snowflake_rsa_key.p8
# In Snowsight: ALTER USER <you> SET RSA_PUBLIC_KEY='<public key body, no headers>';
```

Edit `.env` and fill in at least:

```
SNOWFLAKE_ACCOUNT=<orglocator>-<accountname>
SNOWFLAKE_USER=...
SNOWFLAKE_PRIVATE_KEY_PATH=~/.ssh/snowflake_rsa_key.p8
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=<passphrase>
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DERMIQ_DEV
# SNOWFLAKE_PASSWORD= only if the account doesn't enforce MFA (legacy fallback)
```

Verticals that use the LLM/RAG toolkit (e.g. DermIQ's AI Studio + Canvas) also read
an Anthropic key from this same `.env`; add it here so both repos share it:

```
ANTHROPIC_API_KEY=sk-ant-...   # console.anthropic.com; requires a $10 prepaid minimum
```

## 6. Verify the connection

```bash
python -c "from platform_core.warehouse.connection import test_connection; print(test_connection())"
```

A dict with your Snowflake version/account/user/role/warehouse means everything
is wired correctly. You're ready to set up the vertical — continue in
`dermiq/docs/SETUP.md`.

---

## Troubleshooting

- **`ModuleNotFoundError: platform_core`** — the venv isn't active, or the editable
  install didn't run. Re-activate `.venv` and re-run step 4.
- **Snowflake auth/connection errors** — re-check the `SNOWFLAKE_*` values in `.env`;
  `SNOWFLAKE_ACCOUNT` is `<orglocator>-<accountname>`.
- **Apple Silicon:** the Snowflake Python connector ships arm64 wheels — confirm
  your interpreter is native with `python -c "import platform; print(platform.machine())"`
  (should print `arm64`).
