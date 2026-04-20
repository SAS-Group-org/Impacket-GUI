# ⬡ Impacket GUI

A dark-themed, single-file Tkinter front-end for the [Impacket](https://github.com/fortra/impacket) network protocol toolkit. Build, preview, and execute Impacket commands through a structured GUI — no CLI memorization required.

> **For authorized use only.** Run this tool exclusively on networks and systems you own or have explicit written permission to test.

---

## Screenshot

```
╔══════════════════════════════════════════════════════════╗
║           Impacket GUI  ·  For Authorized Testing        ║
║      Use only on networks you own or have permission     ║
╚══════════════════════════════════════════════════════════╝
```

*Sidebar → Category → Tool tabs → Two-column form → Live terminal output*

---

## Features

- **20+ Impacket tools** organized across 7 categories
- **Live terminal** — streams stdout/stderr in real time
- **Build Command** — preview the exact CLI string before running
- **Copy to clipboard** — paste the command anywhere
- **Kill Process** — terminate long-running tools instantly
- **Password toggle** — show/hide sensitive fields
- **File pickers** — browse for input files and output directories
- **Install checker** — scans PATH for all supported Impacket binaries
- **Session log** — save the full terminal output to disk
- **Zero dependencies** beyond Python 3 and Impacket — no pip extras needed for the GUI itself

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.8 or newer |
| Tkinter | Bundled with most Python installs |
| Impacket | 0.12 or newer (0.10+ should work) |

### Install Impacket

```bash
pip install impacket
```

Or from source for the latest version:

```bash
git clone https://github.com/fortra/impacket.git
cd impacket
pip install .
```

---

## Installation

No installation needed — it's a single script.

```bash
# Clone or download
git clone https://your-repo/impacket-gui.git
cd impacket-gui

# Run
python3 impacket_gui.py
```

### Linux / Kali

Tkinter may need to be installed separately:

```bash
# Debian / Ubuntu / Kali
sudo apt install python3-tk

# Arch
sudo pacman -S tk

# Fedora / RHEL
sudo dnf install python3-tkinter
```

### Windows

Tkinter is bundled with the official Python installer from python.org. No extra steps needed.

### macOS

```bash
brew install python-tk
```

---

## Supported Tools

### Remote Execution

| Tool | Description |
|---|---|
| `psexec` | PSEXEC-like shell via RemComSvc over SMB |
| `smbexec` | Command execution via SMB service — no binary dropped to disk |
| `wmiexec` | Semi-interactive shell over WMI |
| `atexec` | Command execution via Task Scheduler |
| `dcomexec` | DCOM-based semi-interactive shell (MMC20, ShellWindows, ShellBrowserWindow) |

### Kerberos

| Tool | Description |
|---|---|
| `getTGT` | Request a Ticket-Granting Ticket (TGT) |
| `getST` | Request a Service Ticket — supports S4U2Self / S4U2Proxy |
| `getNPUsers` | AS-REP Roasting — dump hashes for accounts with pre-auth disabled |
| `getUserSPNs` | Kerberoasting — enumerate SPNs and request TGS tickets |
| `ticketer` | Forge Golden or Silver Kerberos tickets |

### Credential Dumping

| Tool | Description |
|---|---|
| `secretsdump` | Dump SAM, LSA secrets, NTDS.dit (remote or local) |
| `samrdump` | Enumerate users from SAM via MSRPC |

### SMB / File Shares

| Tool | Description |
|---|---|
| `smbclient` | Interactive SMB client — browse shares, upload/download |
| `smbserver` | Spin up a rogue SMB server (hash capture / file serving) |
| `lookupsid` | Bruteforce SID lookup to enumerate domain users |

### RPC / LDAP

| Tool | Description |
|---|---|
| `rpcdump` | Enumerate RPC endpoints |
| `reg` | Remote Windows Registry operations (query / add / delete) |
| `ldapdomaindump` | Dump Active Directory info via LDAP into JSON / HTML / grep-friendly files |

### MSSQL

| Tool | Description |
|---|---|
| `mssqlclient` | Interactive MSSQL client with `xp_cmdshell` support |
| `mssqlpwner` | MSSQL privilege escalation and linked server abuse |

### Network Recon

| Tool | Description |
|---|---|
| `ping6` | IPv6 ping utility |
| `sniffer` | Simple network packet sniffer |
| `ntlmrelayx` | NTLM relay attacks — works alongside Responder |

---

## Usage

### Workflow

1. **Pick a category** from the left sidebar
2. **Select a tool** from the tab strip at the top
3. **Fill in the fields** — required fields are unlabelled, optional fields show a hint
4. **Build Command** to preview the CLI string in the terminal
5. **Run** to execute, or **Copy** to paste into your own terminal

### Authentication Fields

Most tools share a common authentication pattern:

| Field | Notes |
|---|---|
| Domain | AD domain (e.g. `corp.local`) or `WORKGROUP` for local |
| Username | Account to authenticate as |
| Password | Leave blank if using an NTLM hash |
| NTLM Hash | Format: `LM:NT` — use `aad3b435b51404eeaad3b435b51404ee:` as the LM portion if unknown |
| Kerberos | Uses the `KRB5CCNAME` environment variable (point to a `.ccache` file) |

### Pass-the-Hash Example (secretsdump)

```
Domain:   CORP
Username: Administrator
Password: (leave blank)
NTLM Hash: aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
Target:   192.168.1.10
```

### Checking Your Installation

Go to **Help → Check Impacket Install** to scan PATH for all supported binaries and verify the `impacket` Python library is importable.

---

## Saving Output

- **Help → Save Session Log** writes the full terminal history to a `.txt` file
- Individual tools that support `-outputfile` or `-output` have a dedicated field in the form

---

## Tips

- Use **Kill Process** to stop long-running interactive shells (`psexec`, `smbclient`, `mssqlclient`)
- For Kerberos attacks, set `KRB5CCNAME=/path/to/ticket.ccache` in your shell before launching the GUI
- The **smbserver** tool requires root/admin privileges to bind port 445 — run with `sudo python3 impacket_gui.py` or use a port above 1024 and redirect with `socat`
- `ntlmrelayx` pairs with [Responder](https://github.com/lgandx/Responder) — run Responder separately with SMB/HTTP disabled, then launch the relay from the GUI

---

## Disclaimer

This tool is intended for **authorized penetration testing, CTF competitions, and security research only**.

Unauthorized access to computer systems is illegal and unethical. The authors accept no liability for misuse. Always obtain explicit written permission before testing any system or network you do not own.

---

## Credits

- **Impacket** — [fortra/impacket](https://github.com/fortra/impacket) (formerly SecureAuth Corp)
- GUI built with Python's standard `tkinter` library — no third-party GUI dependencies
