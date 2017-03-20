# -*- coding: utf-8 -*-
"""
Steps for behavioral style tests are defined in this module.
Each step is defined by the string decorating it.
This string is used to call the step in "*.feature" file.
"""
from __future__ import unicode_literals

import pexpect
import os
import re
import sys

from behave import given, when, then


@given('we have mycli installed')
def step_install_cli(_):
    """
    Check that mycli can be started.
    """
    sys.path.append('..')
    try:
        import mycli.main
    except Exception as x:
        raise Exception("Unable to import mycli.main.", x)


@when('we run mycli')
def step_run_cli(context):
    """
    Run the process using pexpect.
    """
    run_args = []
    if context.conf.get('host', None):
        run_args.extend(('-h', context.conf['host']))
    if context.conf.get('user', None):
        run_args.extend(('-u', context.conf['user']))
    if context.conf.get('pass', None):
        run_args.extend(('-p', context.conf['pass']))
    if context.conf.get('dbname', None):
        run_args.extend(('-D', context.conf['dbname']))
    cli_cmd = context.conf.get('cli_command', None) or sys.executable+' -c "import coverage ; coverage.process_startup(); import mycli.main; mycli.main.cli()"'

    cmd_parts = [cli_cmd] + run_args
    cmd = ' '.join(cmd_parts)
    print(cmd)
    context.cli = pexpect.spawnu(cmd, cwd='..')
    context.exit_sent = False


@when('we wait for prompt')
def step_wait_prompt(context):
    """
    Make sure prompt is displayed.
    """
    user = context.conf['user']
    host = context.conf['host']
    dbname = context.conf['dbname']
    _expect_exact(context, 'mysql {0}@{1}:{2}> '.format(user, host, dbname), timeout=5)


@when('we send "ctrl + d"')
def step_ctrl_d(context):
    """
    Send Ctrl + D to hopefully exit.
    """
    context.cli.sendcontrol('d')
    context.exit_sent = True


@when('we send "\?" command')
def step_send_help(context):
    """
    Send \? to see help.
    """
    context.cli.sendline('\\?')


@when('we save a named query')
def step_save_named_query(context):
    """
    Send \ns command
    """
    context.cli.sendline('\\fs foo SELECT 12345')


@when('we use a named query')
def step_use_named_query(context):
    """
    Send \n command
    """
    context.cli.sendline('\\f foo')


@when('we delete a named query')
def step_delete_named_query(context):
    """
    Send \nd command
    """
    context.cli.sendline('\\fd foo')


@when('we create database')
def step_db_create(context):
    """
    Send create database.
    """
    context.cli.sendline('create database {0};'.format(
        context.conf['dbname_tmp']))

    context.response = {
        'database_name': context.conf['dbname_tmp']
    }


@when('we drop database')
def step_db_drop(context):
    """
    Send drop database.
    """
    context.cli.sendline('drop database {0};'.format(
        context.conf['dbname_tmp']))

    _expect_exact(context, 'You\'re about to run a destructive command.\r\nDo you want to proceed? (y/n):', timeout=2)
    context.cli.sendline('y')


@when('we create table')
def step_create_table(context):
    """
    Send create table.
    """
    context.cli.sendline('create table a(x text);')


@when('we insert into table')
def step_insert_into_table(context):
    """
    Send insert into table.
    """
    context.cli.sendline('''insert into a(x) values('xxx');''')


@when('we update table')
def step_update_table(context):
    """
    Send insert into table.
    """
    context.cli.sendline('''update a set x = 'yyy' where x = 'xxx';''')


@when('we select from table')
def step_select_from_table(context):
    """
    Send select from table.
    """
    context.cli.sendline('select * from a;')


@when('we delete from table')
def step_delete_from_table(context):
    """
    Send deete from table.
    """
    context.cli.sendline('''delete from a where x = 'yyy';''')
    _expect_exact(context, 'You\'re about to run a destructive command.\r\nDo you want to proceed? (y/n):', timeout=2)
    context.cli.sendline('y')


@when('we drop table')
def step_drop_table(context):
    """
    Send drop table.
    """
    context.cli.sendline('drop table a;')
    _expect_exact(context, 'You\'re about to run a destructive command.\r\nDo you want to proceed? (y/n):', timeout=2)
    context.cli.sendline('y')


@when('we connect to test database')
def step_db_connect_test(context):
    """
    Send connect to database.
    """
    db_name = context.conf['dbname']
    context.cli.sendline('use {0}'.format(db_name))


@when('we start external editor providing a file name')
def step_edit_file(context):
    """
    Edit file with external editor.
    """
    context.editor_file_name = 'test_file_{0}.sql'.format(context.conf['vi'])
    if os.path.exists(context.editor_file_name):
        os.remove(context.editor_file_name)
    context.cli.sendline('\e {0}'.format(context.editor_file_name))
    _expect_exact(context, 'Entering Ex mode.  Type "visual" to go to Normal mode.', timeout=2)
    _expect_exact(context, '\r\n:', timeout=2)


@when('we type sql in the editor')
def step_edit_type_sql(context):
    context.cli.sendline('i')
    context.cli.sendline('select * from abc')
    context.cli.sendline('.')
    _expect_exact(context, ':', timeout=2)


@when('we exit the editor')
def step_edit_quit(context):
    context.cli.sendline('x')
    _expect_exact(context, "written", timeout=2)


@then('we see the sql in prompt')
def step_edit_done_sql(context):
    _expect_exact(context, 'select\x1b[0m \x1b[0;38;5;241m*\x1b[0m \x1b[0;38;5;28;1mfrom\x1b[0m \x1b[0mabc', timeout=2)
    # Cleanup the command line.
    context.cli.sendcontrol('u')
    # Cleanup the edited file.
    if context.editor_file_name and os.path.exists(context.editor_file_name):
        os.remove(context.editor_file_name)


@when('we connect to mysql')
def step_db_connect_mysql(context):
    """
    Send connect to database.
    """
    context.cli.sendline('use mysql')


@when('we refresh completions')
def step_refresh_completions(context):
    """
    Send refresh command.
    """
    context.cli.sendline('rehash')


@then('mycli exits')
def step_wait_exit(context):
    """
    Make sure the cli exits.
    """
    _expect_exact(context, pexpect.EOF, timeout=5)


@then('we see mycli prompt')
def step_see_prompt(context):
    """
    Wait to see the prompt.
    """
    user = context.conf['user']
    host = context.conf['host']
    dbname = context.conf['dbname']
    _expect_exact(context, 'mysql {0}@{1}:{2}> '.format(user, host, dbname), timeout=5)


@then('we see help output')
def step_see_help(context):
    for expected_line in context.fixture_data['help_commands.txt']:
        _expect_exact(context, expected_line+'\r\n', timeout=1)


@then('we see database created')
def step_see_db_created(context):
    """
    Wait to see create database output.
    """
    _expect_exact(context, 'Query OK, 1 row affected\r\n', timeout=2)


@then('we see database dropped')
def step_see_db_dropped(context):
    """
    Wait to see drop database output.
    """
    _expect_exact(context, 'Query OK, 0 rows affected\r\n', timeout=2)


@then('we see database connected')
def step_see_db_connected(context):
    """
    Wait to see drop database output.
    """
    _expect_exact(context, 'You are now connected to database "', timeout=2)
    _expect_exact(context, '"', timeout=2)
    _expect_exact(context, ' as user "{0}"\r\n'.format(context.conf['user']), timeout=2)


@then('we see table created')
def step_see_table_created(context):
    """
    Wait to see create table output.
    """
    _expect_exact(context, 'Query OK, 0 rows affected\r\n', timeout=2)


@then('we see record inserted')
def step_see_record_inserted(context):
    """
    Wait to see insert output.
    """
    _expect_exact(context, 'Query OK, 1 row affected\r\n', timeout=2)


@then('we see record updated')
def step_see_record_updated(context):
    """
    Wait to see update output.
    """
    _expect_exact(context, 'Query OK, 1 row affected\r\n', timeout=2)


@then('we see data selected')
def step_see_data_selected(context):
    """
    Wait to see select output.
    """
    _expect_exact(context, '+-----+\r\n| x   |\r\n|-----|\r\n| yyy |\r\n+-----+\r\n1 row in set\r\n', timeout=1)


@then('we see record deleted')
def step_see_data_deleted(context):
    """
    Wait to see delete output.
    """
    _expect_exact(context, 'Query OK, 1 row affected\r\n', timeout=2)


@then('we see table dropped')
def step_see_table_dropped(context):
    """
    Wait to see drop output.
    """
    _expect_exact(context, 'Query OK, 0 rows affected\r\n', timeout=2)


@then('we see the named query saved')
def step_see_named_query_saved(context):
    """
    Wait to see query saved.
    """
    _expect_exact(context, 'Saved.\r\n', timeout=1)


@then('we see the named query executed')
def step_see_named_query_executed(context):
    """
    Wait to see select output.
    """
    _expect_exact(context, '12345', timeout=1)
    _expect_exact(context, 'SELECT 1', timeout=1)


@then('we see the named query deleted')
def step_see_named_query_deleted(context):
    """
    Wait to see query deleted.
    """
    _expect_exact(context, 'foo: Deleted', timeout=1)


@then('we see completions refresh started')
def step_see_refresh_started(context):
    """
    Wait to see refresh output.
    """
    _expect_exact(context, 'Auto-completion refresh started in the background', timeout=2)

def _expect_exact(context, expected, timeout):
    try:
        context.cli.expect_exact(expected, timeout=timeout)
    except:
        # Strip color codes out of the output.
        actual = re.sub(r'\x1b\[([0-9A-Za-z;?])+[m|K]?', '', context.cli.before)
        raise Exception('Expected:\n---\n{0!r}\n---\n\nActual:\n---\n{1!r}\n---'.format(
            expected,
            actual))
