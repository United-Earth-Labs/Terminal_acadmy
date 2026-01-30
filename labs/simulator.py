"""
Terminal output simulator for Terminal Academy.

This module provides simulated outputs for various commands
without executing anything on the real system.

SECURITY CRITICAL: This is a SIMULATION ONLY.
No real commands are executed. All output is pre-generated or computed.
"""
import random
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .terminal import ParsedCommand


@dataclass
class SimulatedOutput:
    """Represents the output of a simulated command."""
    output: str
    return_code: int = 0
    is_error: bool = False


class EnvironmentSimulator:
    """
    Simulates a terminal environment with filesystem, network, etc.
    """
    
    def __init__(self, environment_config: Dict = None):
        """
        Initialize the simulator with an environment configuration.
        
        Args:
            environment_config: Configuration dict from SimulatedEnvironment model
        """
        self.config = environment_config or {}
        # Use default filesystem if config doesn't have one or has an empty one
        config_filesystem = self.config.get('filesystem')
        self.filesystem = config_filesystem if config_filesystem else self._default_filesystem()
        self.network = self.config.get('network_config', {})
        self.current_dir = '/home/student'
        self.user = self.config.get('simulated_user', 'student')
        self.hostname = self.config.get('simulated_hostname', 'academy-lab')
        
        # Command handlers
        self.handlers = {
            'ls': self._handle_ls,
            'dir': self._handle_ls,
            'cd': self._handle_cd,
            'pwd': self._handle_pwd,
            'cat': self._handle_cat,
            'head': self._handle_head,
            'tail': self._handle_tail,
            'grep': self._handle_grep,
            'find': self._handle_find,
            'echo': self._handle_echo,
            'whoami': self._handle_whoami,
            'id': self._handle_id,
            'hostname': self._handle_hostname,
            'uname': self._handle_uname,
            'date': self._handle_date,
            'cal': self._handle_cal,
            'nmap': self._handle_nmap,
            'ping': self._handle_ping,
            'traceroute': self._handle_traceroute,
            'netstat': self._handle_netstat,
            'curl': self._handle_curl,
            'wget': self._handle_wget,
            'ssh': self._handle_ssh,
            'nc': self._handle_nc,
            'nslookup': self._handle_nslookup,
            'dig': self._handle_dig,
            'whois': self._handle_whois,
            'file': self._handle_file,
            'strings': self._handle_strings,
            'base64': self._handle_base64,
            'md5sum': self._handle_md5sum,
            'sha256sum': self._handle_sha256sum,
            'history': self._handle_history,
            'clear': self._handle_clear,
            'help': self._handle_help,
            'man': self._handle_man,
        }
        
        self.command_history: List[str] = []
    
    def execute(self, parsed_cmd: ParsedCommand) -> SimulatedOutput:
        """
        Execute a parsed command and return simulated output.
        
        Args:
            parsed_cmd: The parsed command from CommandParser
        
        Returns:
            SimulatedOutput with the result
        """
        if not parsed_cmd.is_valid:
            return SimulatedOutput(
                output=parsed_cmd.error_message,
                return_code=1,
                is_error=True
            )
        
        # Add to history
        self.command_history.append(parsed_cmd.raw_input)
        
        # Get handler
        handler = self.handlers.get(parsed_cmd.command)
        if handler:
            try:
                return handler(parsed_cmd.args)
            except Exception as e:
                return SimulatedOutput(
                    output=f"Error: {str(e)}",
                    return_code=1,
                    is_error=True
                )
        
        return SimulatedOutput(
            output=f"Command not implemented: {parsed_cmd.command}",
            return_code=127,
            is_error=True
        )
    
    def get_prompt(self) -> str:
        """Get the current terminal prompt."""
        return f"{self.user}@{self.hostname}:{self.current_dir}$ "
    
    def _default_filesystem(self) -> Dict:
        """Return a default simulated filesystem."""
        return {
            '/': {'type': 'dir', 'children': ['home', 'etc', 'var', 'tmp']},
            '/home': {'type': 'dir', 'children': ['student']},
            '/home/student': {
                'type': 'dir',
                'children': ['welcome.txt', 'notes.txt', 'scan_results', 'tools', '.secret.txt', '.bashrc']
            },
            '/home/student/welcome.txt': {
                'type': 'file',
                'content': 'Welcome to Terminal Academy!\n\nThis is your first Linux lab environment.\nUse basic commands to explore and complete the objectives.\n\nGood luck!\n'
            },
            '/home/student/notes.txt': {
                'type': 'file',
                'content': 'Welcome to Terminal Academy!\n\nYour first task is to explore this system.\nHint: Hidden files start with a dot (.)\n'
            },
            '/home/student/.secret.txt': {
                'type': 'file',
                'content': '🎉 Congratulations! You found the secret file!\n\nFLAG{found_it}\n\nWell done! You now know how to find hidden files in Linux.\n'
            },
            '/home/student/.bashrc': {
                'type': 'file',
                'content': '# .bashrc\n# User specific aliases and functions\nalias ll="ls -la"\n'
            },
            '/home/student/scan_results': {
                'type': 'dir',
                'children': ['target_192.168.1.100.txt']
            },
            '/home/student/scan_results/target_192.168.1.100.txt': {
                'type': 'file',
                'content': 'Scan completed at 2024-01-15\nOpen ports: 22, 80, 443, 3306\nServices: ssh, http, https, mysql\n'
            },
            '/home/student/tools': {'type': 'dir', 'children': []},
            '/etc': {'type': 'dir', 'children': ['passwd', 'hosts']},
            '/etc/passwd': {
                'type': 'file',
                'content': 'root:x:0:0:root:/root:/bin/bash\nstudent:x:1000:1000:Student:/home/student:/bin/bash\n'
            },
            '/etc/hosts': {
                'type': 'file',
                'content': '127.0.0.1    localhost\n192.168.1.100    target\n192.168.1.1    gateway\n'
            },
            '/var': {'type': 'dir', 'children': ['log']},
            '/var/log': {'type': 'dir', 'children': ['auth.log', 'syslog']},
            '/var/log/auth.log': {
                'type': 'file',
                'content': 'Jan 15 10:00:00 academy-lab sshd[1234]: Failed password for admin from 192.168.1.50\n'
            },
            '/tmp': {'type': 'dir', 'children': []},
        }
    
    def _resolve_path(self, path: str) -> str:
        """Resolve a path relative to current directory."""
        if not path or path == '.':
            return self.current_dir
        if path.startswith('/'):
            return path
        if path == '..':
            parts = self.current_dir.rsplit('/', 1)
            return parts[0] if parts[0] else '/'
        # Handle relative paths
        resolved = f"{self.current_dir}/{path}".replace('//', '/')
        return resolved
    
    def _get_node(self, path: str) -> Optional[Dict]:
        """Get a filesystem node by path."""
        resolved = self._resolve_path(path)
        return self.filesystem.get(resolved)
    
    # Command Handlers
    
    def _handle_ls(self, args: List[str]) -> SimulatedOutput:
        path = args[0] if args else '.'
        show_all = '-a' in args or '-la' in args
        show_long = '-l' in args or '-la' in args
        
        # Remove flags from args
        path = next((a for a in args if not a.startswith('-')), '.')
        
        node = self._get_node(path)
        if not node:
            return SimulatedOutput(f"ls: cannot access '{path}': No such file or directory", 1, True)
        
        if node['type'] != 'dir':
            return SimulatedOutput(path, 0)
        
        children = node.get('children', [])
        if show_all:
            children = ['.', '..'] + children
        
        if show_long:
            output_lines = []
            for child in children:
                child_path = f"{self._resolve_path(path)}/{child}".replace('//', '/')
                child_node = self.filesystem.get(child_path, {'type': 'file'})
                is_dir = child_node.get('type') == 'dir'
                perms = 'drwxr-xr-x' if is_dir else '-rw-r--r--'
                size = len(child_node.get('content', '')) if not is_dir else 4096
                output_lines.append(f"{perms} 1 {self.user} {self.user} {size:>8} Jan 15 10:00 {child}")
            return SimulatedOutput('\n'.join(output_lines), 0)
        
        return SimulatedOutput('  '.join(children), 0)
    
    def _handle_cd(self, args: List[str]) -> SimulatedOutput:
        if not args:
            self.current_dir = f'/home/{self.user}'
            return SimulatedOutput('', 0)
        
        path = self._resolve_path(args[0])
        node = self.filesystem.get(path)
        
        if not node:
            return SimulatedOutput(f"cd: {args[0]}: No such file or directory", 1, True)
        if node['type'] != 'dir':
            return SimulatedOutput(f"cd: {args[0]}: Not a directory", 1, True)
        
        self.current_dir = path
        return SimulatedOutput('', 0)
    
    def _handle_pwd(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput(self.current_dir, 0)
    
    def _handle_cat(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("cat: missing file operand", 1, True)
        
        outputs = []
        for path in args:
            node = self._get_node(path)
            if not node:
                outputs.append(f"cat: {path}: No such file or directory")
            elif node['type'] == 'dir':
                outputs.append(f"cat: {path}: Is a directory")
            else:
                outputs.append(node.get('content', ''))
        
        return SimulatedOutput('\n'.join(outputs), 0)
    
    def _handle_head(self, args: List[str]) -> SimulatedOutput:
        lines = 10
        files = []
        
        for i, arg in enumerate(args):
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                except ValueError:
                    pass
            elif not arg.startswith('-'):
                files.append(arg)
        
        if not files:
            return SimulatedOutput("head: missing file operand", 1, True)
        
        result = self._handle_cat(files)
        if result.is_error:
            return result
        
        output_lines = result.output.split('\n')[:lines]
        return SimulatedOutput('\n'.join(output_lines), 0)
    
    def _handle_tail(self, args: List[str]) -> SimulatedOutput:
        lines = 10
        files = []
        
        for i, arg in enumerate(args):
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                except ValueError:
                    pass
            elif not arg.startswith('-'):
                files.append(arg)
        
        if not files:
            return SimulatedOutput("tail: missing file operand", 1, True)
        
        result = self._handle_cat(files)
        if result.is_error:
            return result
        
        output_lines = result.output.split('\n')[-lines:]
        return SimulatedOutput('\n'.join(output_lines), 0)
    
    def _handle_grep(self, args: List[str]) -> SimulatedOutput:
        if len(args) < 2:
            return SimulatedOutput("Usage: grep PATTERN FILE", 1, True)
        
        pattern = args[0]
        files = args[1:]
        
        results = []
        for path in files:
            node = self._get_node(path)
            if node and node['type'] == 'file':
                content = node.get('content', '')
                for line in content.split('\n'):
                    if pattern.lower() in line.lower():
                        if len(files) > 1:
                            results.append(f"{path}:{line}")
                        else:
                            results.append(line)
        
        if results:
            return SimulatedOutput('\n'.join(results), 0)
        return SimulatedOutput('', 1)
    
    def _handle_find(self, args: List[str]) -> SimulatedOutput:
        start_path = args[0] if args else '.'
        results = []
        
        for path in self.filesystem:
            if path.startswith(self._resolve_path(start_path)):
                results.append(path)
        
        return SimulatedOutput('\n'.join(sorted(results)), 0)
    
    def _handle_echo(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput(' '.join(args), 0)
    
    def _handle_whoami(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput(self.user, 0)
    
    def _handle_id(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput(f"uid=1000({self.user}) gid=1000({self.user}) groups=1000({self.user})", 0)
    
    def _handle_hostname(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput(self.hostname, 0)
    
    def _handle_uname(self, args: List[str]) -> SimulatedOutput:
        if '-a' in args:
            return SimulatedOutput("Linux academy-lab 5.15.0-generic #1 SMP x86_64 GNU/Linux", 0)
        return SimulatedOutput("Linux", 0)
    
    def _handle_date(self, args: List[str]) -> SimulatedOutput:
        now = datetime.datetime.now()
        return SimulatedOutput(now.strftime("%a %b %d %H:%M:%S UTC %Y"), 0)
    
    def _handle_cal(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput("""    January 2024
Su Mo Tu We Th Fr Sa
    1  2  3  4  5  6
 7  8  9 10 11 12 13
14 15 16 17 18 19 20
21 22 23 24 25 26 27
28 29 30 31""", 0)
    
    def _handle_nmap(self, args: List[str]) -> SimulatedOutput:
        """Simulated nmap scan - the key feature!"""
        if not args:
            return SimulatedOutput("Usage: nmap [options] target", 1, True)
        
        target = args[-1]  # Last arg is usually target
        
        # Get simulated network data
        hosts = self.network.get('hosts', {})
        host_data = hosts.get(target)
        
        output = f"""Starting Nmap 7.94 ( https://nmap.org ) at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
Nmap scan report for {target}
Host is up (0.0015s latency).

PORT      STATE    SERVICE     VERSION
"""
        
        if host_data:
            # Use our config format: ports is a dict of port -> {service, banner}
            ports_data = host_data.get('ports', {})
            for port, info in sorted(ports_data.items(), key=lambda x: int(x[0])):
                service = info.get('service', 'unknown')
                banner = info.get('banner', '')
                output += f"{port}/tcp   open     {service:<12}{banner}\n"
        else:
            # Default scan results for unknown hosts
            output += """22/tcp    open     ssh         OpenSSH 8.9
80/tcp    open     http        Apache httpd 2.4
443/tcp   open     https       
"""
        
        output += f"""
Nmap done: 1 IP address (1 host up) scanned in 2.45 seconds"""
        
        return SimulatedOutput(output, 0)
    
    def _default_host_scan(self) -> Dict:
        """Default scan results for unknown hosts."""
        return {
            'ports': {
                '22': {'service': 'ssh', 'banner': 'OpenSSH 8.9'},
                '80': {'service': 'http', 'banner': 'Apache httpd 2.4'},
                '443': {'service': 'https', 'banner': ''},
            }
        }
    
    def _handle_ping(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: ping target", 1, True)
        
        target = args[-1]
        output = f"""PING {target} 56(84) bytes of data.
64 bytes from {target}: icmp_seq=1 ttl=64 time=0.5 ms
64 bytes from {target}: icmp_seq=2 ttl=64 time=0.4 ms
64 bytes from {target}: icmp_seq=3 ttl=64 time=0.5 ms

--- {target} ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 0.4/0.47/0.5/0.04 ms"""
        return SimulatedOutput(output, 0)
    
    def _handle_traceroute(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: traceroute target", 1, True)
        
        target = args[-1]
        output = f"""traceroute to {target}, 30 hops max, 60 byte packets
 1  gateway (192.168.1.1)  0.5 ms  0.4 ms  0.3 ms
 2  10.0.0.1  1.2 ms  1.1 ms  1.0 ms
 3  {target}  2.5 ms  2.4 ms  2.3 ms"""
        return SimulatedOutput(output, 0)
    
    def _handle_netstat(self, args: List[str]) -> SimulatedOutput:
        output = """Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
tcp        0      0 192.168.1.10:45678      192.168.1.100:80        ESTABLISHED"""
        return SimulatedOutput(output, 0)
    
    def _handle_curl(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("curl: no URL specified", 1, True)
        
        url = args[-1]
        
        # Simulated HTTP response
        output = """<!DOCTYPE html>
<html>
<head><title>Target Web Server</title></head>
<body>
<h1>Welcome to the Target Server</h1>
<p>This is a simulated web page for training purposes.</p>
<!-- TODO: Remove debug info before production -->
<!-- Admin panel: /admin -->
</body>
</html>"""
        return SimulatedOutput(output, 0)
    
    def _handle_wget(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("wget: missing URL", 1, True)
        
        url = args[-1]
        return SimulatedOutput(f"""--2024-01-15 10:00:00--  {url}
Resolving target... 192.168.1.100
Connecting to target|192.168.1.100|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1234 (1.2K) [text/html]
Saving to: 'index.html'

index.html          100%[===================>]   1.2K  --.-KB/s    in 0s      

2024-01-15 10:00:00 (50.0 MB/s) - 'index.html' saved [1234/1234]""", 0)
    
    def _handle_ssh(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput("ssh: Simulated connection - interactive SSH is not available in this lab", 0)
    
    def _handle_nc(self, args: List[str]) -> SimulatedOutput:
        if len(args) < 2:
            return SimulatedOutput("Usage: nc host port", 1, True)
        
        host = args[0]
        port = args[1] if len(args) > 1 else '80'
        return SimulatedOutput(f"Connection to {host} {port} port [tcp/*] succeeded!", 0)
    
    def _handle_nslookup(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: nslookup hostname", 1, True)
        
        host = args[0]
        output = f"""Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	{host}
Address: 192.168.1.100"""
        return SimulatedOutput(output, 0)
    
    def _handle_dig(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: dig hostname", 1, True)
        
        host = args[0]
        output = f"""; <<>> DiG 9.18.1 <<>> {host}
;; ANSWER SECTION:
{host}.		300	IN	A	192.168.1.100

;; Query time: 10 msec
;; SERVER: 8.8.8.8#53(8.8.8.8)"""
        return SimulatedOutput(output, 0)
    
    def _handle_whois(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: whois domain", 1, True)
        
        domain = args[0]
        output = f"""Domain Name: {domain.upper()}
Registry Domain ID: 123456789
Registrar: Example Registrar, Inc.
Created Date: 2020-01-01T00:00:00Z
Registrant Organization: Example Corp
Registrant Country: US"""
        return SimulatedOutput(output, 0)
    
    def _handle_file(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: file filename", 1, True)
        
        path = args[0]
        node = self._get_node(path)
        
        if not node:
            return SimulatedOutput(f"{path}: cannot open (No such file)", 1, True)
        
        if node['type'] == 'dir':
            return SimulatedOutput(f"{path}: directory", 0)
        
        return SimulatedOutput(f"{path}: ASCII text", 0)
    
    def _handle_strings(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: strings filename", 1, True)
        
        return SimulatedOutput("Simulated strings output: No printable strings found", 0)
    
    def _handle_base64(self, args: List[str]) -> SimulatedOutput:
        import base64
        
        if '-d' in args:
            # Decode
            text = args[-1] if args[-1] != '-d' else ''
            try:
                decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                return SimulatedOutput(decoded, 0)
            except:
                return SimulatedOutput("base64: invalid input", 1, True)
        else:
            # Encode
            text = args[-1] if args else ''
            encoded = base64.b64encode(text.encode()).decode()
            return SimulatedOutput(encoded, 0)
    
    def _handle_md5sum(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: md5sum filename", 1, True)
        
        # Simulated hash
        return SimulatedOutput(f"d41d8cd98f00b204e9800998ecf8427e  {args[0]}", 0)
    
    def _handle_sha256sum(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: sha256sum filename", 1, True)
        
        # Simulated hash
        return SimulatedOutput(f"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  {args[0]}", 0)
    
    def _handle_history(self, args: List[str]) -> SimulatedOutput:
        output_lines = [f"  {i+1}  {cmd}" for i, cmd in enumerate(self.command_history[-50:])]
        return SimulatedOutput('\n'.join(output_lines), 0)
    
    def _handle_clear(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput('\033[2J\033[H', 0)  # ANSI clear screen
    
    def _handle_help(self, args: List[str]) -> SimulatedOutput:
        return SimulatedOutput("""Terminal Academy Lab Environment

Available commands:
  ls, cd, pwd, cat, head, tail, grep, find, echo
  whoami, id, hostname, uname, date, cal
  nmap, ping, traceroute, netstat, curl, wget
  ssh, nc, nslookup, dig, whois
  file, strings, base64, md5sum, sha256sum
  history, clear, help, man

Type 'man <command>' for detailed help on a specific command.""", 0)
    
    def _handle_man(self, args: List[str]) -> SimulatedOutput:
        if not args:
            return SimulatedOutput("Usage: man command", 1, True)
        
        manpages = {
            'nmap': """NMAP(1)                          Nmap Reference Guide

NAME
       nmap - Network exploration tool and security / port scanner

SYNOPSIS
       nmap [Options] target

DESCRIPTION
       Nmap is a utility for network discovery and security auditing.
       
       In this simulated environment, nmap will scan pre-configured 
       target systems and return realistic-looking results.

EXAMPLES
       nmap target
       nmap -sV target
       nmap -p 22,80,443 target
""",
            'grep': """GREP(1)                          User Commands

NAME
       grep - print lines that match patterns

SYNOPSIS
       grep PATTERN FILE

DESCRIPTION
       grep searches for PATTERN in each FILE.
""",
        }
        
        cmd = args[0].lower()
        if cmd in manpages:
            return SimulatedOutput(manpages[cmd], 0)
        
        return SimulatedOutput(f"No manual entry for {cmd}", 1, True)
