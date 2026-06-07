# Setup Guide

End-to-end setup from a fresh machine to a working `platform-core` development environment. Tested on Windows 11 + WSL2 + Ubuntu 24.04, but the Ubuntu steps work on native Linux too.

## Prerequisites

- A Windows 10/11 machine, a Mac, or a Linux machine
- A GitHub account
- About 60 minutes for first-time setup

## What you'll have at the end

- A Linux development environment (WSL2 on Windows, native on Mac/Linux)
- Python 3.12, Node.js 20, Docker, git, AWS CLI, Astronomer CLI installed and working
- This repo cloned with a working virtual environment
- SSH keys connecting your machine to GitHub

## 1. Set up WSL2 (Windows only — skip if on Mac/Linux)

WSL2 (Windows Subsystem for Linux) gives you a real Linux environment inside Windows. The data engineering tooling (dbt, Airflow, Docker) is built primarily for Linux.

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Reboot when prompted. After reboot, an Ubuntu terminal opens automatically and asks for a username and password. The password won't show as you type — that's normal.

Verify:

```bash
echo "I am inside Linux on $(date)"
```

Quirks to know:
- Paste into terminal = right-click your mouse (not Ctrl+V)
- Copy = highlight text with your mouse (auto-copies)

## 2. Install Docker Desktop with WSL integration

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Open Docker Desktop, click the gear icon (Settings) → Resources → WSL integration
4. Enable the toggle for your Ubuntu distro
5. Click Apply & restart

Verify from inside Ubuntu:

```bash
docker run --rm hello-world
```

If you get "permission denied":

```bash
sudo usermod -aG docker $USER && newgrp docker
```

## 3. Install development tools

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl wget unzip build-essential
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs
cd ~ && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip -q awscliv2.zip && sudo ./aws/install && rm -rf aws awscliv2.zip
curl -sSL install.astronomer.io | sudo bash -s
```

Verify everything:

```bash
python3 --version
node --version
git --version
aws --version
astro version
docker --version
```

## 4. Configure git identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.editor "nano"
```

## 5. Set up SSH keys for GitHub

```bash
ssh-keygen -t ed25519 -C "your-github-email@example.com"
```

Press Enter for all three prompts.

Print the public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

In your browser:
1. Go to https://github.com/settings/keys
2. Click New SSH key
3. Paste the entire public key line (including the email at the end)
4. Click Add SSH key

Test:

```bash
ssh -T git@github.com
```

Type `yes` when asked about host authenticity. Expected output:

```
Hi <your-github-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

## 6. Clone the repo

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:pneiman1/platform-core.git
cd platform-core
```

## 7. Set up the Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[all]"
```

Verify:

```bash
python -c "import platform_core; print(platform_core.__version__)"
```

Should print `0.1.0`.

## 8. Install VS Code with the WSL extension

Install VS Code from https://code.visualstudio.com/. Then install these extensions:

- WSL (by Microsoft)
- Python (by Microsoft)
- dbt Power User (by Innoverio)
- Tailwind CSS IntelliSense (by Tailwind Labs)
- Prettier - Code formatter

To connect VS Code to WSL: press `Ctrl+Shift+P`, type `WSL: Connect to WSL`, press Enter.

## Troubleshooting

**Docker says "permission denied"**

```bash
sudo usermod -aG docker $USER && newgrp docker
```

**`ssh -T git@github.com` says "Permission denied (publickey)"**

The public key on GitHub doesn't match your local private key. Compare them.

**`pip install -e ".[all]"` is slow**

Prophet, xgboost, and sentence-transformers compile from source. Be patient. If stuck, install in smaller groups: `pip install -e ".[api]"` then `pip install -e ".[ml]"`, etc.

## What's next

- [`DECISIONS.md`](DECISIONS.md) — architecture decision log