import os
import sys
import argparse
import getpass
from pykeepass import PyKeePass

DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), '.keypass', '.kp.kdbx')
DEFAULT_PATH = 'EnvVars'
DEFAULT_FIELD = 'value'

def sys_exit(message, exit_code=0, stderr=True):
    """ print message and system exit with exit code
    """
    args = {}
    if stderr:
        args['file'] = sys.stderr
    print(message, **args)
    sys.exit(exit_code)

def parse_args():
    """
    Parse command-line arguments for with-keypass.

    Returns:
        argparse.Namespace: parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='with-keypass',
        description='Execute a command with environment variables loaded from KeePass.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--db',
        dest='db_path',
        default=DEFAULT_DB_PATH,
        help='Path to KeePass .kdbx database file')
    parser.add_argument(
        '--path',
        dest='path',
        default=DEFAULT_PATH,
        help='path to KeePass entry or KeePass group containing the secrets to load')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print NAME=value pairs and exit; do not exec a command')
    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        help='Command to execute; must be preceded by -- (not required with --dry-run)')

    args = parser.parse_args()

    # Require explicit `--` separator before command unless dry-run
    if args.command and args.command[0] == '--':
        args.command = args.command[1:]
    elif not args.dry_run and not args.command:
        parser.error('You must specify a command after \'--\' (or use --dry-run).')

    return args

def _env_from_group(group, path):
    """ return environment variables dict from keepass group
    """
    env_vars = {}
    for entry in group.entries:
        entry_name = (entry.title or '').strip()
        if not entry_name:
            continue
        value = entry.get_custom_property(DEFAULT_FIELD)
        if not value:
            continue
        env_vars[entry_name] = str(value)

    if not env_vars:
        sys_exit(f'No environment variables found in KeePass group {path}.', exit_code=2)

    return env_vars

def _env_from_entry(entry, path):
    """ return custom properties dict from keepass entry
    """
    if not entry.custom_properties:
        sys_exit(f'No key value attributes found in KeePass entry {path}.', exit_code=2)
    return entry.custom_properties

def get_env_keypass(db_path, password, path):
    """ retrieve environment variables from KeePass entries.
    """
    try:
        keepass = PyKeePass(db_path, password=password)
    except Exception as error:
        sys_exit(f'Failed to open KeePass DB: {error}', exit_code=1)

    path_split = path.split('/')
    group = keepass.find_groups_by_path(path_split, first=True)
    entry = keepass.find_entries_by_path(path_split, first=True)

    if group is not None:
        return _env_from_group(group, path)
    elif entry is not None:
        return _env_from_entry(entry, path)

    sys_exit(f'The path {path} was neither a group or entry', exit_code=2)

def get_password():
    """ get password from envvar if present otherwise prompt for password
    """
    password = os.getenv('KEEPASS_PASSWORD')
    if not password:
        password = getpass.getpass('Enter KeePass master password: ')
    return password

def _main():
    """ main function
    """
    args = parse_args()

    try:
        master_password = get_password()
    except (KeyboardInterrupt, EOFError):
        sys_exit('\nAborted', exit_code=130)

    env_vars = get_env_keypass(
        args.db, master_password, args.group_name, args.field_name, args.entry_path)

    if args.dry_run:
        for key, value in env_vars.items():
            print(f'{key}={value}')
        sys.exit(0)

    merged_env_vars = dict(os.environ)
    merged_env_vars.update(env_vars)

    os.execvpe(args.command[0], args.command, merged_env_vars)

def main():
    """ entry point for with-keypass
    """
    sys.exit(_main())

if __name__ == '__main__':
    main()
