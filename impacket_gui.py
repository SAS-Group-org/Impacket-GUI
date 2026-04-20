#!/usr/bin/env python3
"""
Impacket GUI — A comprehensive Tkinter front-end for the Impacket toolkit.
Requires: Python 3.8+, Tkinter (usually bundled), Impacket installed in PATH.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import shutil
import os
import json
from datetime import datetime

# ─── Colour palette ──────────────────────────────────────────────────────────
BG        = "#0d1117"
PANEL     = "#161b22"
SIDEBAR   = "#0d1117"
CARD      = "#1c2128"
BORDER    = "#30363d"
ACCENT    = "#58a6ff"
ACCENT2   = "#3fb950"
WARN      = "#f78166"
TEXT      = "#e6edf3"
TEXT_DIM  = "#8b949e"
ENTRY_BG  = "#21262d"
ENTRY_FG  = TEXT
SEL       = "#264f78"
TAG_OK    = "#3fb950"
TAG_ERR   = "#f78166"
TAG_CMD   = "#d2a8ff"
TAG_INFO  = "#58a6ff"

FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_H1   = ("Segoe UI Semibold", 13)
FONT_H2   = ("Segoe UI Semibold", 10)
FONT_SM   = ("Segoe UI", 9)

# ─── Tool definitions ─────────────────────────────────────────────────────────
# Each tool has: name, binary, description, fields[]
# Field: (label, key, type, default, hint)
#   type: entry | password | check | combo | file

TOOLS = {
    "Remote Execution": [
        {
            "name": "psexec",
            "binary": "impacket-psexec",
            "alt_binary": "python3 -m impacket.examples.psexec",
            "desc": "PSEXEC-like functionality using RemComSvc over SMB.",
            "fields": [
                ("Domain",       "domain",   "entry",    "",        "WORKGROUP or AD domain"),
                ("Username",     "username", "entry",    "",        "e.g. Administrator"),
                ("Password",     "password", "password", "",        "Leave blank to use hash"),
                ("NTLM Hash",    "hashes",   "entry",    "",        "LM:NT  (optional)"),
                ("Target Host",  "target",   "entry",    "",        "IP or hostname"),
                ("Command",      "command",  "entry",    "cmd.exe", "Command to run (default: cmd.exe)"),
                ("Port",         "port",     "entry",    "445",     "SMB port"),
                ("No Pass",      "no-pass",  "check",    False,     "Skip password auth"),
                ("Kerberos",     "-k",       "check",    False,     "Use Kerberos auth"),
            ],
            "build": lambda f: _build_auth_cmd("impacket-psexec", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-port", "port"), ("-c", "command")],
                flags=[("-no-pass", "no-pass"), ("-k", "-k")]),
        },
        {
            "name": "smbexec",
            "binary": "impacket-smbexec",
            "desc": "Executes commands via SMB using a service — no binary drop.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",        ""),
                ("Username",    "username", "entry",    "",        ""),
                ("Password",    "password", "password", "",        ""),
                ("NTLM Hash",   "hashes",   "entry",    "",        "LM:NT"),
                ("Target Host", "target",   "entry",    "",        ""),
                ("Share",       "share",    "entry",    "ADMIN$",  "Remote share to use"),
                ("Kerberos",    "-k",       "check",    False,     ""),
                ("No Pass",     "no-pass",  "check",    False,     ""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-smbexec", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-share", "share")],
                flags=[("-k", "-k"), ("-no-pass", "no-pass")]),
        },
        {
            "name": "wmiexec",
            "binary": "impacket-wmiexec",
            "desc": "Semi-interactive shell using Windows Management Instrumentation.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",        ""),
                ("Username",    "username", "entry",    "",        ""),
                ("Password",    "password", "password", "",        ""),
                ("NTLM Hash",   "hashes",   "entry",    "",        "LM:NT"),
                ("Target Host", "target",   "entry",    "",        ""),
                ("Command",     "command",  "entry",    "",        "Single command (optional)"),
                ("Share",       "share",    "entry",    "ADMIN$",  ""),
                ("Kerberos",    "-k",       "check",    False,     ""),
                ("No Pass",     "no-pass",  "check",    False,     ""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-wmiexec", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-share", "share")],
                flags=[("-k", "-k"), ("-no-pass", "no-pass")],
                trailing="command"),
        },
        {
            "name": "atexec",
            "binary": "impacket-atexec",
            "desc": "Execute commands via Task Scheduler (AT service).",
            "fields": [
                ("Domain",      "domain",   "entry",    "",   ""),
                ("Username",    "username", "entry",    "",   ""),
                ("Password",    "password", "password", "",   ""),
                ("NTLM Hash",   "hashes",   "entry",    "",   "LM:NT"),
                ("Target Host", "target",   "entry",    "",   ""),
                ("Command",     "command",  "entry",    "whoami", "Command to execute"),
                ("Kerberos",    "-k",       "check",    False,""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-atexec", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes")],
                flags=[("-k", "-k")],
                trailing="command"),
        },
        {
            "name": "dcomexec",
            "binary": "impacket-dcomexec",
            "desc": "DCOM-based semi-interactive shell.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",       ""),
                ("Username",    "username", "entry",    "",       ""),
                ("Password",    "password", "password", "",       ""),
                ("NTLM Hash",   "hashes",   "entry",    "",       "LM:NT"),
                ("Target Host", "target",   "entry",    "",       ""),
                ("Command",     "command",  "entry",    "",       "Single command (optional)"),
                ("Object",      "object",   "combo",    "MMC20", ["MMC20", "ShellWindows", "ShellBrowserWindow"]),
                ("Kerberos",    "-k",       "check",    False,    ""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-dcomexec", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-object", "object")],
                flags=[("-k", "-k")],
                trailing="command"),
        },
    ],
    "Kerberos": [
        {
            "name": "GetTGT",
            "binary": "impacket-getTGT",
            "desc": "Request a Ticket-Granting Ticket (TGT) for an account.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  "FQDN e.g. corp.local"),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  "LM:NT (for PTH)"),
                ("AES Key",     "aesKey",   "entry",    "",  "128 or 256 bit AES key"),
                ("DC IP",       "dc-ip",    "entry",    "",  "Domain Controller IP"),
                ("Output File", "output",   "entry",    "ticket.ccache", "Save TGT to file"),
            ],
            "build": lambda f: _build_kerb_cmd("impacket-getTGT", f),
        },
        {
            "name": "GetST",
            "binary": "impacket-getST",
            "desc": "Request a Service Ticket (ST) — supports S4U2Self/S4U2Proxy.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  ""),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  "LM:NT"),
                ("AES Key",     "aesKey",   "entry",    "",  ""),
                ("DC IP",       "dc-ip",    "entry",    "",  ""),
                ("SPN",         "spn",      "entry",    "",  "e.g. cifs/server.corp.local"),
                ("Impersonate", "impersonate","entry",  "",  "User to impersonate (S4U2Proxy)"),
                ("Output File", "output",   "entry",    "ticket.ccache", ""),
            ],
            "build": lambda f: _build_kerb_cmd("impacket-getST", f, extra_flags=[("-spn", "spn"), ("-impersonate", "impersonate")]),
        },
        {
            "name": "GetNPUsers",
            "binary": "impacket-getNPUsers",
            "desc": "AS-REP Roasting — dump hashes for accounts with pre-auth disabled.",
            "fields": [
                ("Domain",       "domain",    "entry",  "",  ""),
                ("Username",     "username",  "entry",  "",  "Single user (or blank for all)"),
                ("Password",     "password",  "password","", ""),
                ("NTLM Hash",    "hashes",    "entry",  "",  ""),
                ("DC IP",        "dc-ip",     "entry",  "",  ""),
                ("User File",    "usersfile", "file",   "",  "File with usernames"),
                ("Request",      "request",   "check",  True,"Request TGT for vulnerable accounts"),
                ("Format",       "format",    "combo",  "hashcat", ["hashcat", "john"]),
                ("Output File",  "outputfile","entry",  "",  "Save results to file"),
            ],
            "build": lambda f: _build_npusers_cmd(f),
        },
        {
            "name": "GetUserSPNs",
            "binary": "impacket-getUserSPNs",
            "desc": "Kerberoasting — enumerate & request SPNs to crack offline.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  ""),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  ""),
                ("DC IP",       "dc-ip",    "entry",    "",  ""),
                ("Request",     "request",  "check",    True,"Request TGS for each SPN"),
                ("Format",      "format",   "combo",    "hashcat", ["hashcat", "john"]),
                ("Output File", "outputfile","entry",   "",  ""),
            ],
            "build": lambda f: _build_spns_cmd(f),
        },
        {
            "name": "ticketer",
            "binary": "impacket-ticketer",
            "desc": "Create Golden / Silver Kerberos tickets.",
            "fields": [
                ("Username",    "user",     "entry",    "",  "Account name for the ticket"),
                ("Domain",      "domain",   "entry",    "",  "Domain FQDN"),
                ("Domain SID",  "domain-sid","entry",   "",  "e.g. S-1-5-21-..."),
                ("NTLM Hash",   "nthash",   "entry",    "",  "krbtgt hash (Golden) or service (Silver)"),
                ("AES 128",     "aesKey128","entry",    "",  ""),
                ("AES 256",     "aesKey256","entry",    "",  ""),
                ("SPN",         "spn",      "entry",    "",  "For Silver ticket e.g. cifs/srv"),
                ("Extra SIDs",  "extra-sid","entry",    "",  "Comma-separated SIDs"),
                ("Duration",    "duration", "entry",    "10","Ticket lifetime in hours"),
            ],
            "build": lambda f: _build_ticketer_cmd(f),
        },
    ],
    "Credential Dumping": [
        {
            "name": "secretsdump",
            "binary": "impacket-secretsdump",
            "desc": "Dump SAM, LSA secrets, NTDS.dit — remotely or from local files.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  ""),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  "LM:NT"),
                ("Target Host", "target",   "entry",    "",  "IP/hostname or LOCAL"),
                ("DC IP",       "dc-ip",    "entry",    "",  "For NTDS dump via drsuapi"),
                ("Output File", "outputfile","entry",   "",  "Prefix for output files"),
                ("Just DC",     "just-dc",  "check",    False,"Only dump NTDS.dit"),
                ("Just DC NTLMs","just-dc-ntlm","check",False,"Only NTLM hashes from NTDS"),
                ("Just DC User","just-dc-user","entry", "",  "Dump specific user only"),
                ("Use VSS",     "use-vss",  "check",    False,"Use VSS instead of drsuapi"),
                ("Kerberos",    "-k",       "check",    False,""),
                ("No Pass",     "no-pass",  "check",    False,""),
            ],
            "build": lambda f: _build_secretsdump_cmd(f),
        },
        {
            "name": "samrdump",
            "binary": "impacket-samrdump",
            "desc": "Enumerate users from the SAM database via MSRPC.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  ""),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  ""),
                ("Target Host", "target",   "entry",    "",  ""),
                ("CSV File",    "csv",      "entry",    "",  "Save results as CSV"),
                ("Kerberos",    "-k",       "check",    False,""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-samrdump", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-csv", "csv")],
                flags=[("-k", "-k")]),
        },
    ],
    "SMB / File Shares": [
        {
            "name": "smbclient",
            "binary": "impacket-smbclient",
            "desc": "Interactive SMB client — browse shares, upload/download files.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",  ""),
                ("Username",    "username", "entry",    "",  ""),
                ("Password",    "password", "password", "",  ""),
                ("NTLM Hash",   "hashes",   "entry",    "",  ""),
                ("Target Host", "target",   "entry",    "",  ""),
                ("Kerberos",    "-k",       "check",    False,""),
                ("No Pass",     "no-pass",  "check",    False,""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-smbclient", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes")],
                flags=[("-k", "-k"), ("-no-pass", "no-pass")]),
        },
        {
            "name": "smbserver",
            "binary": "impacket-smbserver",
            "desc": "Spin up a quick SMB server to receive files / capture hashes.",
            "fields": [
                ("Share Name",  "sharename","entry",    "SHARE",  "Name of the SMB share"),
                ("Share Path",  "sharepath","file",     ".",      "Local folder to serve"),
                ("IP",          "ip",       "entry",    "0.0.0.0","Bind IP"),
                ("Port",        "port",     "entry",    "445",    "Bind port"),
                ("SMB2 Support","-smb2support","check", True,     "Enable SMB2"),
                ("Username",    "username", "entry",    "",       "Require auth (optional)"),
                ("Password",    "password", "password", "",       ""),
            ],
            "build": lambda f: _build_smbserver_cmd(f),
        },
        {
            "name": "lookupsid",
            "binary": "impacket-lookupsid",
            "desc": "Bruteforce SID lookup to enumerate domain users.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",      ""),
                ("Username",    "username", "entry",    "",      ""),
                ("Password",    "password", "password", "",      ""),
                ("NTLM Hash",   "hashes",   "entry",    "",      ""),
                ("Target Host", "target",   "entry",    "",      ""),
                ("Max RID",     "maxRid",   "entry",    "4000",  "Max RID to bruteforce"),
                ("Kerberos",    "-k",       "check",    False,   ""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-lookupsid", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-maxRid", "maxRid")],
                flags=[("-k", "-k")]),
        },
    ],
    "RPC / LDAP": [
        {
            "name": "rpcdump",
            "binary": "impacket-rpcdump",
            "desc": "Enumerate RPC endpoints on a target.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",   ""),
                ("Username",    "username", "entry",    "",   ""),
                ("Password",    "password", "password", "",   ""),
                ("NTLM Hash",   "hashes",   "entry",    "",   ""),
                ("Target Host", "target",   "entry",    "",   ""),
                ("Port",        "port",     "entry",    "135",""),
                ("Protocol",    "proto",    "combo",    "ncacn_ip_tcp", ["ncacn_ip_tcp", "ncacn_np"]),
            ],
            "build": lambda f: _build_auth_cmd("impacket-rpcdump", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-port", "port"), ("-proto", "proto")],
                flags=[]),
        },
        {
            "name": "reg",
            "binary": "impacket-reg",
            "desc": "Remote Windows Registry operations via MSRPC.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",      ""),
                ("Username",    "username", "entry",    "",      ""),
                ("Password",    "password", "password", "",      ""),
                ("NTLM Hash",   "hashes",   "entry",    "",      ""),
                ("Target Host", "target",   "entry",    "",      ""),
                ("Action",      "action",   "combo",    "query", ["query", "add", "delete"]),
                ("Key Path",    "keyName",  "entry",    "HKLM\\SYSTEM\\CurrentControlSet", "Registry key"),
                ("Value",       "valueName","entry",    "",      "Value name (optional)"),
            ],
            "build": lambda f: _build_reg_cmd(f),
        },
        {
            "name": "ldapdomaindump",
            "binary": "ldapdomaindump",
            "desc": "Dump Active Directory info via LDAP into JSON/HTML/Grep files.",
            "fields": [
                ("Domain",      "domain",      "entry",    "",  ""),
                ("Username",    "username",    "entry",    "",  ""),
                ("Password",    "password",    "password", "",  ""),
                ("DC Host",     "dc-host",     "entry",    "",  "DC hostname or IP"),
                ("Output Dir",  "directory",   "file",     ".",  "Output directory"),
                ("No HTML",     "no-html",     "check",    False,""),
                ("No JSON",     "no-json",     "check",    False,""),
                ("No Grep",     "no-grep",     "check",    False,""),
            ],
            "build": lambda f: _build_ldap_cmd(f),
        },
    ],
    "MSSQL": [
        {
            "name": "mssqlclient",
            "binary": "impacket-mssqlclient",
            "desc": "Interactive MSSQL client with xp_cmdshell support.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",    ""),
                ("Username",    "username", "entry",    "",    ""),
                ("Password",    "password", "password", "",    ""),
                ("NTLM Hash",   "hashes",   "entry",    "",    ""),
                ("Target Host", "target",   "entry",    "",    ""),
                ("Port",        "port",     "entry",    "1433",""),
                ("Instance",    "db",       "entry",    "",    "Database (optional)"),
                ("Windows Auth","-windows-auth","check",True,  "Use Windows Authentication"),
                ("Kerberos",    "-k",       "check",    False, ""),
            ],
            "build": lambda f: _build_auth_cmd("impacket-mssqlclient", f,
                positional="{domain}/{username}:{password}@{target}",
                extras=[("-hashes", "hashes"), ("-port", "port"), ("-db", "db")],
                flags=[("-windows-auth", "-windows-auth"), ("-k", "-k")]),
        },
        {
            "name": "mssqlpwner",
            "binary": "impacket-mssqlpwner",
            "desc": "MSSQL privilege escalation & linked server abuse.",
            "fields": [
                ("Domain",      "domain",   "entry",    "",    ""),
                ("Username",    "username", "entry",    "",    ""),
                ("Password",    "password", "password", "",    ""),
                ("NTLM Hash",   "hashes",   "entry",    "",    ""),
                ("Target Host", "target",   "entry",    "",    ""),
                ("Port",        "port",     "entry",    "1433",""),
                ("Action",      "action",   "combo",    "enumerate",
                    ["enumerate", "exec", "rev-shell", "upload-exec"]),
                ("Command",     "command",  "entry",    "",    "Command for exec/rev-shell"),
            ],
            "build": lambda f: _build_mssqlpwner_cmd(f),
        },
    ],
    "Network Recon": [
        {
            "name": "ping6",
            "binary": "impacket-ping6",
            "desc": "IPv6 ping utility (part of Impacket examples).",
            "fields": [
                ("Target Host", "target",   "entry",    "",  "IPv6 address or hostname"),
                ("Count",       "count",    "entry",    "4", "Number of echo requests"),
            ],
            "build": lambda f: f"impacket-ping6 {f.get('count','')} {f.get('target','')}".strip(),
        },
        {
            "name": "sniff",
            "binary": "impacket-sniffer",
            "desc": "Simple network packet sniffer.",
            "fields": [
                ("Interface",   "interface","entry",    "eth0","Network interface"),
                ("Filter",      "filter",   "entry",    "",   "BPF filter (optional)"),
            ],
            "build": lambda f: f"impacket-sniffer -iface {f['interface']}" +
                               (f" -filter \"{f['filter']}\"" if f.get("filter") else ""),
        },
        {
            "name": "ntlmrelayx",
            "binary": "impacket-ntlmrelayx",
            "desc": "NTLM relay attacks — pair with Responder for credential capture.",
            "fields": [
                ("Target(s)",   "tf",       "file",     "",  "File of target IPs/URLs (-tf)"),
                ("Single Target","-t",       "entry",    "",  "Single target URL"),
                ("SMB2 Support","-smb2support","check",  True, ""),
                ("Interactive", "-i",       "check",    False,"Interactive shell mode"),
                ("SOCKS",       "-socks",   "check",    False,"SOCKS proxy mode"),
                ("Auto-inject", "-e",       "file",     "",  "Inject this exe on relay"),
                ("Command",     "-c",       "entry",    "",  "Command on successful relay"),
                ("Domain Admin Check","-da","check",    False,"Stop after relaying domain admin"),
                ("HTTP Port",   "-http-port","entry",   "80", ""),
                ("HTTPS Port",  "-https-port","entry",  "443",""),
            ],
            "build": lambda f: _build_ntlmrelayx_cmd(f),
        },
    ],
}

# ─── Command builders ─────────────────────────────────────────────────────────

def _build_auth_cmd(binary, f, positional="", extras=None, flags=None, trailing=None):
    domain   = f.get("domain", "")
    username = f.get("username", "")
    password = f.get("password", "")
    target   = f.get("target", "")

    target_str = positional.format(
        domain=domain, username=username,
        password=password, target=target
    )
    # Clean up empties: remove password from string if blank
    if not password:
        target_str = target_str.replace(f":{password}", "")

    parts = [binary, target_str]

    for flag, key in (extras or []):
        val = f.get(key, "")
        if val:
            parts += [flag, val]

    for flag, key in (flags or []):
        if f.get(key):
            parts.append(flag)

    if trailing and f.get(trailing):
        parts.append(f.get(trailing))

    return " ".join(parts)


def _build_kerb_cmd(binary, f, extra_flags=None):
    parts = [binary,
             f"{f.get('domain','')}/{f.get('username','')}",
             f"-password {f.get('password','')}" if f.get("password") else ""]
    for k, v in [("-hashes", "hashes"), ("-aesKey", "aesKey"),
                 ("-dc-ip", "dc-ip"), ("-output", "output")]:
        if f.get(v):
            parts += [k, f.get(v)]
    for flag, key in (extra_flags or []):
        if f.get(key):
            parts += [flag, f.get(key)]
    return " ".join(p for p in parts if p)


def _build_npusers_cmd(f):
    target = f"{f.get('domain','')}/{f.get('username','')}:{f.get('password','')}"
    parts = ["impacket-getNPUsers", target]
    if f.get("hashes"):    parts += ["-hashes", f["hashes"]]
    if f.get("dc-ip"):     parts += ["-dc-ip", f["dc-ip"]]
    if f.get("usersfile"): parts += ["-usersfile", f["usersfile"]]
    if f.get("request"):   parts.append("-request")
    if f.get("format"):    parts += ["-format", f["format"]]
    if f.get("outputfile"):parts += ["-outputfile", f["outputfile"]]
    return " ".join(parts)


def _build_spns_cmd(f):
    target = f"{f.get('domain','')}/{f.get('username','')}"
    if f.get("password"):
        target += f":{f['password']}"
    parts = ["impacket-getUserSPNs", target]
    if f.get("hashes"):     parts += ["-hashes", f["hashes"]]
    if f.get("dc-ip"):      parts += ["-dc-ip", f["dc-ip"]]
    if f.get("request"):    parts.append("-request")
    if f.get("format"):     parts += ["-format", f["format"]]
    if f.get("outputfile"): parts += ["-outputfile", f["outputfile"]]
    return " ".join(parts)


def _build_ticketer_cmd(f):
    parts = ["impacket-ticketer", f"-nthash {f['nthash']}" if f.get("nthash") else ""]
    if f.get("aesKey128"): parts += ["-aesKey", f["aesKey128"]]
    if f.get("aesKey256"): parts += ["-aesKey", f["aesKey256"]]
    if f.get("domain-sid"):parts += ["-domain-sid", f["domain-sid"]]
    if f.get("domain"):    parts += ["-domain", f["domain"]]
    if f.get("spn"):       parts += ["-spn", f["spn"]]
    if f.get("extra-sid"): parts += ["-extra-sid", f["extra-sid"]]
    if f.get("duration"):  parts += ["-duration", f["duration"]]
    if f.get("user"):      parts.append(f["user"])
    return " ".join(p for p in parts if p)


def _build_secretsdump_cmd(f):
    target = f"{f.get('domain','')}/{f.get('username','')}"
    if f.get("password"): target += f":{f['password']}"
    target += f"@{f.get('target','')}"
    parts = ["impacket-secretsdump", target]
    if f.get("hashes"):         parts += ["-hashes", f["hashes"]]
    if f.get("dc-ip"):          parts += ["-dc-ip", f["dc-ip"]]
    if f.get("outputfile"):     parts += ["-outputfile", f["outputfile"]]
    if f.get("just-dc"):        parts.append("-just-dc")
    if f.get("just-dc-ntlm"):   parts.append("-just-dc-ntlm")
    if f.get("just-dc-user"):   parts += ["-just-dc-user", f["just-dc-user"]]
    if f.get("use-vss"):        parts.append("-use-vss")
    if f.get("-k"):             parts.append("-k")
    if f.get("no-pass"):        parts.append("-no-pass")
    return " ".join(parts)


def _build_smbserver_cmd(f):
    parts = ["impacket-smbserver"]
    if f.get("-smb2support"): parts.append("-smb2support")
    if f.get("ip"):           parts += ["-ip", f["ip"]]
    if f.get("port") and f["port"] != "445":
        parts += ["-port", f["port"]]
    if f.get("username") and f.get("password"):
        parts += ["-username", f["username"], "-password", f["password"]]
    parts.append(f.get("sharename", "SHARE"))
    parts.append(f.get("sharepath", "."))
    return " ".join(parts)


def _build_reg_cmd(f):
    target = f"{f.get('domain','')}/{f.get('username','')}"
    if f.get("password"): target += f":{f['password']}"
    target += f"@{f.get('target','')}"
    parts = ["impacket-reg", target, f.get("action","query"), f.get("keyName","")]
    if f.get("valueName"): parts += ["-v", f["valueName"]]
    if f.get("hashes"):    parts += ["-hashes", f["hashes"]]
    return " ".join(parts)


def _build_ldap_cmd(f):
    parts = ["ldapdomaindump"]
    if f.get("username") and f.get("domain"):
        parts += ["-u", f"{f['domain']}\\{f['username']}"]
    if f.get("password"): parts += ["-p", f["password"]]
    if f.get("dc-host"):  parts += ["-d", f["dc-host"]]
    if f.get("directory"):parts += ["-o", f["directory"]]
    if f.get("no-html"):  parts.append("--no-html")
    if f.get("no-json"):  parts.append("--no-json")
    if f.get("no-grep"):  parts.append("--no-grep")
    if f.get("dc-host"):  parts.append(f["dc-host"])
    return " ".join(parts)


def _build_mssqlpwner_cmd(f):
    target = f"{f.get('domain','')}/{f.get('username','')}"
    if f.get("password"): target += f":{f['password']}"
    target += f"@{f.get('target','')}"
    parts = ["impacket-mssqlpwner", target, f.get("action","enumerate")]
    if f.get("hashes"):  parts += ["-hashes", f["hashes"]]
    if f.get("port") and f["port"] != "1433": parts += ["-port", f["port"]]
    if f.get("command"): parts += ["-c", f["command"]]
    return " ".join(parts)


def _build_ntlmrelayx_cmd(f):
    parts = ["impacket-ntlmrelayx"]
    if f.get("tf"):            parts += ["-tf", f["tf"]]
    if f.get("-t"):            parts += ["-t", f["-t"]]
    if f.get("-smb2support"):  parts.append("-smb2support")
    if f.get("-i"):            parts.append("-i")
    if f.get("-socks"):        parts.append("-socks")
    if f.get("-e"):            parts += ["-e", f["-e"]]
    if f.get("-c"):            parts += ["-c", f["-c"]]
    if f.get("-da"):           parts.append("-da")
    if f.get("-http-port") and f["-http-port"] != "80":
        parts += ["-http-port", f["-http-port"]]
    if f.get("-https-port") and f["-https-port"] != "443":
        parts += ["-https-port", f["-https-port"]]
    return " ".join(parts)


# ─── Main Application ─────────────────────────────────────────────────────────

class ImpacketGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Impacket GUI  ·  v1.0")
        self.configure(bg=BG)
        self.minsize(1100, 720)
        self.geometry("1280x800")

        self._current_tool = None
        self._field_vars   = {}
        self._proc         = None
        self._session_log  = []

        self._build_styles()
        self._build_layout()
        self._select_category(list(TOOLS.keys())[0])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Styles ────────────────────────────────────────────────────────────────
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",       background=BG)
        s.configure("Card.TFrame",  background=CARD)
        s.configure("Panel.TFrame", background=PANEL)
        s.configure("TLabel",       background=BG,   foreground=TEXT,     font=FONT_UI)
        s.configure("Card.TLabel",  background=CARD, foreground=TEXT,     font=FONT_UI)
        s.configure("Dim.TLabel",   background=CARD, foreground=TEXT_DIM, font=FONT_SM)
        s.configure("H1.TLabel",    background=PANEL,foreground=TEXT,     font=FONT_H1)
        s.configure("Accent.TLabel",background=PANEL,foreground=ACCENT,   font=FONT_H2)
        s.configure("TCheckbutton", background=CARD, foreground=TEXT,
                    selectcolor=ENTRY_BG, font=FONT_UI,
                    indicatorcolor=CARD, indicatorrelief="flat")
        s.configure("TCombobox",    fieldbackground=ENTRY_BG, background=CARD,
                    foreground=TEXT,     selectbackground=SEL, font=FONT_UI)
        s.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)])
        s.configure("Sash",         background=BORDER)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Menu bar
        menu = tk.Menu(self, bg=PANEL, fg=TEXT, activebackground=SEL,
                       activeforeground=TEXT, relief="flat", borderwidth=0)
        file_menu = tk.Menu(menu, tearoff=0, bg=PANEL, fg=TEXT,
                            activebackground=SEL, activeforeground=TEXT)
        file_menu.add_command(label="Save Session Log", command=self._save_log)
        file_menu.add_command(label="Clear Output",     command=self._clear_output)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",             command=self._on_close)
        menu.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=0, bg=PANEL, fg=TEXT,
                            activebackground=SEL, activeforeground=TEXT)
        help_menu.add_command(label="Check Impacket Install", command=self._check_install)
        help_menu.add_command(label="About",                  command=self._show_about)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

        # ── Root pane (sidebar | main)
        root_pane = tk.PanedWindow(self, orient="horizontal",
                                   bg=BORDER, sashwidth=1, sashrelief="flat")
        root_pane.pack(fill="both", expand=True)

        # ── Sidebar
        self._sidebar = tk.Frame(root_pane, bg=SIDEBAR, width=190)
        root_pane.add(self._sidebar, minsize=160)

        tk.Label(self._sidebar, text="⬡ IMPACKET GUI",
                 bg=SIDEBAR, fg=ACCENT, font=("Courier New", 11, "bold"),
                 pady=14).pack(fill="x", padx=12)

        sep = tk.Frame(self._sidebar, bg=BORDER, height=1)
        sep.pack(fill="x", padx=0)

        self._cat_buttons = {}
        for cat in TOOLS:
            btn = tk.Label(self._sidebar, text=cat, bg=SIDEBAR, fg=TEXT_DIM,
                           font=FONT_UI, anchor="w", padx=16, pady=8,
                           cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>",   lambda e, b=btn: b.config(fg=TEXT, bg=PANEL))
            btn.bind("<Leave>",   lambda e, b=btn, cat=cat: b.config(
                fg=ACCENT if self._current_cat == cat else TEXT_DIM,
                bg=PANEL if self._current_cat == cat else SIDEBAR))
            btn.bind("<Button-1>",lambda e, c=cat: self._select_category(c))
            self._cat_buttons[cat] = btn

        self._current_cat = list(TOOLS.keys())[0]

        # version at bottom
        tk.Label(self._sidebar, text="impacket ≥ 0.12", bg=SIDEBAR,
                 fg=TEXT_DIM, font=FONT_SM).pack(side="bottom", pady=8)

        # ── Main area (top pane | terminal)
        right_frame = tk.Frame(root_pane, bg=BG)
        root_pane.add(right_frame, minsize=700)

        vpane = tk.PanedWindow(right_frame, orient="vertical",
                               bg=BORDER, sashwidth=1, sashrelief="flat")
        vpane.pack(fill="both", expand=True)

        # Tool picker + form
        top_frame = tk.Frame(vpane, bg=BG)
        vpane.add(top_frame, minsize=300)

        # Tool picker strip
        picker_frame = tk.Frame(top_frame, bg=PANEL, pady=0)
        picker_frame.pack(fill="x")

        self._tool_strip_frame = tk.Frame(picker_frame, bg=PANEL)
        self._tool_strip_frame.pack(fill="x", padx=8, pady=6)

        # Tool form (scrollable)
        form_outer = tk.Frame(top_frame, bg=BG)
        form_outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(form_outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._form_inner = tk.Frame(canvas, bg=BG)
        self._canvas_window = canvas.create_window((0, 0), window=self._form_inner,
                                                    anchor="nw")
        self._form_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._canvas_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Terminal
        term_frame = tk.Frame(vpane, bg=BG)
        vpane.add(term_frame, minsize=200)

        term_header = tk.Frame(term_frame, bg=PANEL, pady=4)
        term_header.pack(fill="x")
        tk.Label(term_header, text=" ▶  Output Terminal", bg=PANEL, fg=ACCENT,
                 font=FONT_H2).pack(side="left", padx=10)
        tk.Button(term_header, text="Clear", bg=CARD, fg=TEXT_DIM,
                  relief="flat", font=FONT_SM, cursor="hand2",
                  command=self._clear_output, activebackground=BORDER,
                  activeforeground=TEXT).pack(side="right", padx=6)
        tk.Button(term_header, text="Kill Process", bg=CARD, fg=WARN,
                  relief="flat", font=FONT_SM, cursor="hand2",
                  command=self._kill_proc, activebackground=BORDER,
                  activeforeground=WARN).pack(side="right", padx=2)

        self._output = scrolledtext.ScrolledText(
            term_frame, bg="#0a0e13", fg=TEXT, font=FONT_MONO,
            insertbackground=ACCENT, relief="flat", borderwidth=0,
            wrap="word", state="disabled"
        )
        self._output.pack(fill="both", expand=True, padx=0, pady=0)

        # Tags
        self._output.tag_config("cmd",  foreground=TAG_CMD)
        self._output.tag_config("ok",   foreground=TAG_OK)
        self._output.tag_config("err",  foreground=TAG_ERR)
        self._output.tag_config("info", foreground=TAG_INFO)
        self._output.tag_config("dim",  foreground=TEXT_DIM)

        self._print_banner()

    # ── Sidebar category selection ────────────────────────────────────────────
    def _select_category(self, cat):
        self._current_cat = cat
        for c, btn in self._cat_buttons.items():
            btn.config(fg=ACCENT if c == cat else TEXT_DIM,
                       bg=PANEL  if c == cat else SIDEBAR)

        # Rebuild tool strip
        for w in self._tool_strip_frame.winfo_children():
            w.destroy()
        tk.Label(self._tool_strip_frame, text=cat + "   ›",
                 bg=PANEL, fg=TEXT_DIM, font=FONT_SM).pack(side="left")

        self._tool_btns = {}
        first = None
        for tool in TOOLS[cat]:
            name = tool["name"]
            btn  = tk.Label(self._tool_strip_frame, text=name, bg=CARD,
                            fg=TEXT_DIM, font=FONT_UI, padx=12, pady=4,
                            cursor="hand2", relief="flat")
            btn.pack(side="left", padx=4)
            btn.bind("<Enter>",    lambda e, b=btn: b.config(bg=SEL, fg=TEXT))
            btn.bind("<Leave>",    lambda e, b=btn, n=name: b.config(
                bg=ACCENT if self._current_tool and self._current_tool["name"]==n else CARD,
                fg=BG     if self._current_tool and self._current_tool["name"]==n else TEXT_DIM))
            btn.bind("<Button-1>", lambda e, t=tool: self._select_tool(t))
            self._tool_btns[name] = btn
            if first is None: first = tool

        if first: self._select_tool(first)

    # ── Tool selection & form build ───────────────────────────────────────────
    def _select_tool(self, tool):
        self._current_tool = tool

        # Highlight button
        for n, btn in self._tool_btns.items():
            active = n == tool["name"]
            btn.config(bg=ACCENT if active else CARD,
                       fg=BG     if active else TEXT_DIM)

        # Clear form
        for w in self._form_inner.winfo_children():
            w.destroy()
        self._field_vars = {}

        # Header card
        hdr = tk.Frame(self._form_inner, bg=PANEL, pady=10)
        hdr.pack(fill="x", padx=0, pady=(0, 1))
        tk.Label(hdr, text=tool["name"], bg=PANEL, fg=TEXT, font=FONT_H1,
                 padx=16).pack(side="left")
        tk.Label(hdr, text=tool.get("binary",""), bg=PANEL, fg=ACCENT2,
                 font=FONT_MONO, padx=8).pack(side="left")
        tk.Label(hdr, text=tool.get("desc",""), bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SM, wraplength=700, justify="left",
                 padx=16).pack(side="left", fill="x", expand=True)

        # Fields
        fields_frame = tk.Frame(self._form_inner, bg=BG)
        fields_frame.pack(fill="both", expand=True, padx=16, pady=8)

        fields = tool.get("fields", [])
        # Two-column layout
        col_left  = tk.Frame(fields_frame, bg=BG)
        col_right = tk.Frame(fields_frame, bg=BG)
        col_left.pack(side="left", fill="both", expand=True, padx=(0,8))
        col_right.pack(side="left",fill="both", expand=True, padx=(8,0))

        for i, field in enumerate(fields):
            label, key, ftype, default, hint = field[:5]
            extra = field[5] if len(field) > 5 else None

            parent = col_left if i % 2 == 0 else col_right
            card = tk.Frame(parent, bg=CARD, pady=6, padx=10)
            card.pack(fill="x", pady=4)

            lbl_row = tk.Frame(card, bg=CARD)
            lbl_row.pack(fill="x")
            tk.Label(lbl_row, text=label, bg=CARD, fg=TEXT,
                     font=FONT_H2, anchor="w").pack(side="left")
            if hint:
                tk.Label(lbl_row, text=hint, bg=CARD, fg=TEXT_DIM,
                         font=FONT_SM).pack(side="left", padx=6)

            if ftype == "entry":
                var = tk.StringVar(value=default)
                ent = tk.Entry(card, textvariable=var, bg=ENTRY_BG, fg=ENTRY_FG,
                               insertbackground=ACCENT, relief="flat",
                               font=FONT_MONO, bd=0)
                ent.pack(fill="x", pady=(4,2), ipady=5)
                self._field_vars[key] = var

            elif ftype == "password":
                var = tk.StringVar(value=default)
                row = tk.Frame(card, bg=CARD)
                row.pack(fill="x", pady=(4,2))
                ent = tk.Entry(row, textvariable=var, show="●", bg=ENTRY_BG,
                               fg=ENTRY_FG, insertbackground=ACCENT,
                               relief="flat", font=FONT_MONO, bd=0)
                ent.pack(side="left", fill="x", expand=True, ipady=5)
                show_var = tk.BooleanVar(value=False)
                def toggle(e=ent, sv=show_var):
                    sv.set(not sv.get())
                    e.config(show="" if sv.get() else "●")
                tk.Label(row, text="👁", bg=ENTRY_BG, fg=TEXT_DIM,
                         cursor="hand2", padx=4).pack(side="right")
                row.winfo_children()[-1].bind("<Button-1>", lambda e, t=toggle: t())
                self._field_vars[key] = var

            elif ftype == "check":
                var = tk.BooleanVar(value=bool(default))
                cb  = tk.Checkbutton(card, variable=var, bg=CARD,
                                     activebackground=CARD, fg=TEXT,
                                     selectcolor=ACCENT, cursor="hand2",
                                     relief="flat", bd=0, text="Enabled",
                                     font=FONT_SM, foreground=TEXT_DIM)
                cb.pack(anchor="w", pady=(4,0))
                self._field_vars[key] = var

            elif ftype == "combo":
                var = tk.StringVar(value=default)
                values = extra if isinstance(extra, list) else []
                cb = ttk.Combobox(card, textvariable=var, values=values,
                                  state="readonly", font=FONT_MONO)
                cb.pack(fill="x", pady=(4,2))
                self._field_vars[key] = var

            elif ftype == "file":
                var = tk.StringVar(value=default)
                row = tk.Frame(card, bg=CARD)
                row.pack(fill="x", pady=(4,2))
                ent = tk.Entry(row, textvariable=var, bg=ENTRY_BG, fg=ENTRY_FG,
                               insertbackground=ACCENT, relief="flat",
                               font=FONT_MONO, bd=0)
                ent.pack(side="left", fill="x", expand=True, ipady=5)
                tk.Button(row, text="…", bg=BORDER, fg=TEXT_DIM, relief="flat",
                          font=FONT_SM, cursor="hand2",
                          command=lambda v=var: v.set(
                              filedialog.askopenfilename() or v.get()
                          )).pack(side="right", padx=(4,0), ipadx=6)
                self._field_vars[key] = var

        # Action bar
        action_bar = tk.Frame(self._form_inner, bg=PANEL, pady=10)
        action_bar.pack(fill="x", padx=0, pady=(8,0))

        tk.Button(action_bar, text="  ⌘  Build Command",
                  bg=CARD, fg=TEXT_DIM, font=FONT_UI, relief="flat",
                  cursor="hand2", padx=14, pady=6,
                  activebackground=BORDER, activeforeground=TEXT,
                  command=self._build_and_show).pack(side="left", padx=10)

        tk.Button(action_bar, text="  ▶  Run",
                  bg=ACCENT, fg=BG, font=("Segoe UI Semibold", 10),
                  relief="flat", cursor="hand2", padx=20, pady=6,
                  activebackground="#79c0ff", activeforeground=BG,
                  command=self._run_tool).pack(side="left", padx=4)

        tk.Button(action_bar, text="  ⎘  Copy",
                  bg=CARD, fg=TEXT_DIM, font=FONT_UI, relief="flat",
                  cursor="hand2", padx=12, pady=6,
                  activebackground=BORDER, activeforeground=TEXT,
                  command=self._copy_cmd).pack(side="left", padx=4)

        tk.Button(action_bar, text="  ↺  Reset Fields",
                  bg=CARD, fg=TEXT_DIM, font=FONT_UI, relief="flat",
                  cursor="hand2", padx=12, pady=6,
                  activebackground=BORDER, activeforeground=TEXT,
                  command=lambda: self._select_tool(tool)).pack(side="right", padx=10)

    # ── Command helpers ───────────────────────────────────────────────────────
    def _get_field_values(self):
        return {k: (v.get() if isinstance(v, (tk.StringVar, tk.BooleanVar)) else v)
                for k, v in self._field_vars.items()}

    def _get_command(self):
        if not self._current_tool:
            return ""
        try:
            return self._current_tool["build"](self._get_field_values())
        except Exception as exc:
            return f"# Error building command: {exc}"

    def _build_and_show(self):
        cmd = self._get_command()
        self._log(f"$ {cmd}\n", "cmd")

    def _copy_cmd(self):
        cmd = self._get_command()
        self.clipboard_clear()
        self.clipboard_append(cmd)
        self._log(f"[Copied to clipboard]\n", "info")

    # ── Execution ─────────────────────────────────────────────────────────────
    def _run_tool(self):
        cmd = self._get_command()
        if not cmd or cmd.startswith("#"):
            messagebox.showerror("Error", "Cannot build a valid command.")
            return

        self._log(f"\n{'─'*60}\n", "dim")
        self._log(f"[{datetime.now().strftime('%H:%M:%S')}] Running:\n", "info")
        self._log(f"$ {cmd}\n\n", "cmd")
        self._session_log.append(f"$ {cmd}")

        # Check binary exists
        binary = cmd.split()[0]
        if not shutil.which(binary):
            self._log(f"[!] '{binary}' not found in PATH.\n", "err")
            self._log("    Install Impacket:  pip install impacket\n", "err")
            return

        def worker():
            try:
                self._proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True
                )
                for line in self._proc.stdout:
                    self._log(line, "ok" if not line.startswith("[!]") else "err")
                    self._session_log.append(line.rstrip())
                self._proc.wait()
                rc = self._proc.returncode
                self._log(f"\n[Process exited with code {rc}]\n", "info" if rc==0 else "err")
            except Exception as ex:
                self._log(f"[Error] {ex}\n", "err")
            finally:
                self._proc = None

        threading.Thread(target=worker, daemon=True).start()

    def _kill_proc(self):
        if self._proc:
            self._proc.kill()
            self._log("\n[!] Process killed by user.\n", "warn" if hasattr(self,"warn") else "err")
        else:
            self._log("[No running process]\n", "dim")

    # ── Output ────────────────────────────────────────────────────────────────
    def _log(self, text, tag=""):
        def _do():
            self._output.config(state="normal")
            if tag:
                self._output.insert("end", text, tag)
            else:
                self._output.insert("end", text)
            self._output.see("end")
            self._output.config(state="disabled")
        self.after(0, _do)

    def _clear_output(self):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.config(state="disabled")
        self._print_banner()

    def _print_banner(self):
        banner = (
            "╔══════════════════════════════════════════════════════════╗\n"
            "║           Impacket GUI  ·  For Authorized Testing        ║\n"
            "║      Use only on networks you own or have permission     ║\n"
            "╚══════════════════════════════════════════════════════════╝\n\n"
        )
        self._log(banner, "dim")

    # ── Misc ──────────────────────────────────────────────────────────────────
    def _save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files","*.txt"),("All","*.*")],
            title="Save Session Log"
        )
        if path:
            with open(path, "w") as f:
                f.write("\n".join(self._session_log))
            self._log(f"[Log saved to {path}]\n", "info")

    def _check_install(self):
        self._clear_output()
        self._log("Checking Impacket installation…\n\n", "info")

        tools_to_check = [
            "impacket-psexec","impacket-smbexec","impacket-wmiexec",
            "impacket-secretsdump","impacket-getTGT","impacket-getUserSPNs",
            "impacket-getNPUsers","impacket-smbclient","impacket-ntlmrelayx",
            "impacket-mssqlclient",
        ]

        def worker():
            import importlib.util
            imp = importlib.util.find_spec("impacket")
            if imp:
                self._log("✔  impacket Python library found\n", "ok")
            else:
                self._log("✘  impacket not installed  →  pip install impacket\n", "err")

            self._log("\nCLI tools:\n", "info")
            for t in tools_to_check:
                found = shutil.which(t)
                if found:
                    self._log(f"  ✔  {t:<35} {found}\n", "ok")
                else:
                    self._log(f"  ✘  {t}\n", "err")

        threading.Thread(target=worker, daemon=True).start()

    def _show_about(self):
        messagebox.showinfo(
            "About Impacket GUI",
            "Impacket GUI  v1.0\n\n"
            "A Tkinter front-end for the Impacket network protocol toolkit.\n\n"
            "Impacket is developed by SecureAuth Corp / fortra.\n"
            "This GUI is for authorized penetration testing only.\n\n"
            "github.com/fortra/impacket"
        )

    def _on_close(self):
        if self._proc:
            self._proc.kill()
        self.destroy()


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ImpacketGUI()
    app.mainloop()
