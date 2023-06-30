from argparse import ArgumentParser
# reference: https://docs.python.org/3/library/argparse.html
import pexpect
# reference: https://pexpect.readthedocs.io/en/stable/index.html
from re import (
    search as re_search,
    DOTALL
)
# reference: https://docs.python.org/3/howto/regex.html

USERNAME = None
PASSWORD = None
IP = None
PROTOCOL = None
PORT = None


def parse_arguments():

    global USERNAME
    global PASSWORD
    global IP
    global PROTOCOL
    global PORT

    parser = ArgumentParser(description='Python for testing engineers')
    parser.add_argument('--username', help="the username to authenticate as",
                        required=False, default='admin', dest='username')
    parser.add_argument('--password', help="Used for password authentication",
                        required=False, default='', dest='password')
    parser.add_argument('--ip', help="the switch ip to connect to",
                        required=True, dest='ip')
    parser.add_argument('--protocol', help="ssh|telnet",
                        required=False, default='ssh', dest='protocol')
    parser.add_argument('--port', help="the port number to contact",
                        required=False, default='22', dest='port')

    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.password
    IP = args.ip
    PROTOCOL = args.protocol
    PORT = args.port


parse_arguments()

print(f'''Going to use following parameters:
\tusername: "{USERNAME}"
\tpassword: "{PASSWORD}"
\tip: "{IP}"
\tprotocol: "{PROTOCOL}"
\tport: "{PORT}"''')

print(f'''Trying to connect to "{IP}" using "{PROTOCOL}" ({PORT})
with username: "{USERNAME}" and password: "{PASSWORD}"''')

if 'telnet' in PROTOCOL:
    connection = pexpect.spawn(f'{PROTOCOL} {IP} {PORT}')
    connection.sendline()
    connection.expect('login: $')
    connection.sendline(USERNAME)
    connection.expect('Password:')
elif 'ssh' in PROTOCOL:
    connection = pexpect.spawn(f'{PROTOCOL} {USERNAME}@{IP} -p {PORT}')
    match = connection.expect(['continue connecting \(yes/no\)\?\s','password:'])
    if match == 0:
        connection.sendline('yes')
else:
    print(f'Unknown protocol given "{PROTOCOL}"\n,valid options are only "ssh" or "telnet"')
    exit(1)

connection.sendline(PASSWORD)
connection.expect('[#$]')
print('Connected!')
connection.sendline('show version')
connection.expect('[#$]')
cmd_output = connection.before.decode('utf-8')
print(f'command output: {cmd_output}\n')

show_version_re = (
    'Version\s*:\s*(?P<version>\S+).*'
    'Build\sDate\s*:\s*(?P<build_date>\d+-\d+-\d+\s\d+:\d+:\d+\s\S+).*'
    'Build\sID\s*:\s*(?P<build_id>\S+).*'
    'Build\sSHA\s*:\s*\S+.*'
    'Hot\s+Patches\s*:\s*(?P<hot_patches>\S+)?.*'
    'Active\sImage\s*:\s*(?P<active_image>\S+).*'
    'Service\sOS\sVersion\s*:\s*(?P<service_os_version>\S+).*'
    'BIOS\sVersion\s*:\s(?P<bios_version>\S+)'
)

result = {}
re_result = re_search(show_version_re, cmd_output, DOTALL)
assert re_result, "Unable to parse command output"
result = re_result.groupdict()

print('Parsing results:\n')
for key, value in result.items():
    print(f'{key} : {value}')

print('\nBye!')
connection.sendline('exit')
if 'telnet' in PROTOCOL:
    connection.expect('login: $')
connection.close()
