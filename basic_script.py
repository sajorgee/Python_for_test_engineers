from argparse import ArgumentParser
# reference: https://docs.python.org/3/library/argparse.html

USERNAME = 'admin'
PASSWORD = ''
IP = ''


def parse_arguments():

    global USERNAME
    global PASSWORD
    global IP

    parser = ArgumentParser(description='Python for testing engineers')
    parser.add_argument('--username', help="the username to authenticate as",
                        required=False, default='admin', dest='username')
    parser.add_argument('--password', help="Used for password authentication",
                        required=False, default='', dest='password')
    parser.add_argument('--ip', help="the switch ip to connect to",
                        required=True, dest='ip')

    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.password
    IP = args.ip


parse_arguments()

print(f'Got following arguments: username: "{USERNAME}", password: "{PASSWORD}", ip: "{IP}"')