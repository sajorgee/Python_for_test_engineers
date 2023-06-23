from argparse import ArgumentParser
# reference: https://docs.python.org/3/library/argparse.html
import pexpect
# reference: https://pexpect.readthedocs.io/en/stable/index.html

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
output = connection.before.decode('utf-8')
print(output)
print('Bye!')
connection.sendline('exit')
if 'telnet' in PROTOCOL:
    connection.expect('login: $')
connection.close()
