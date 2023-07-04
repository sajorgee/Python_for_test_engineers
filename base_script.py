from argparse import ArgumentParser
# reference: https://docs.python.org/3/library/argparse.html
import pexpect
# reference: https://pexpect.readthedocs.io/en/stable/index.html
from re import (
    search as re_search,
    DOTALL
)
# reference: https://docs.python.org/3/howto/regex.html
from os.path import isfile

USERNAME = None
PASSWORD = None
IP = None
PROTOCOL = None
PORT = None

COMMANDS_FILE = 'commands.txt'
OUTPUT_FILE = 'output.txt'

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

show_system_re = (
    'Hostname\s*:\s*(?P<hostname>\S+).*'
    'System\s+Description\s*:\s*(?P<description>\S+).*'
    'System\s*Contact\s*:\s*(?P<contact>\S+)?.*System'
)


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


def parse_show_system(connection):
    connection.sendline('show system')
    connection.expect('[#$]')
    cmd_output = connection.before.decode('utf-8')
    print(f'command output: {cmd_output}\n')

    result = {}
    re_result = re_search(show_system_re, cmd_output, DOTALL)
    assert re_result, "Unable to parse command output"
    result = re_result.groupdict()

    print('Parsing results:\n')
    for key, value in result.items():
        print(f'{key} : {value}')


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

    fout = open('mylog.txt','wb')
    connection.logfile = fout

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

parse_show_system(connection)

connection.sendline('no page')
connection.expect('[#$]')

print('\nRead and execute commands from file...\n')

if isfile(COMMANDS_FILE):
    cmd_file = open(COMMANDS_FILE, 'r')
    for line in cmd_file:
        print(f'sending command: {line.strip()}')
        connection.sendline(line.strip())
        connection.expect('[#$]')

cmd_output = connection.before.decode('utf-8')

connection.sendline('show running-config')
connection.expect('[#$]', timeout=60)
cmd_output = connection.before.decode('utf-8')

output_file = open(OUTPUT_FILE, 'w')
for line in cmd_output:
    output_file.write(line)

print('\nBye!')
connection.sendline('exit')
if 'telnet' in PROTOCOL:
    connection.expect('login: $')

connection.close()
