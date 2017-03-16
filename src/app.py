#!/usr/bin/env python3

import sys
import getopt
import os

import pvcheck
import parser
import testdata
import formatter
import jsonformatter
import csvformatter
import executor
import valgrind
import i18n


__doc__ = i18n.HELP_en
_ = i18n.translate

_DEFAULT_LOG_FILE = os.path.expanduser("~/.pvcheck.log")


def parse_options():
    """Parse the command line."""

    shortopts = "hc:t:v:m:C:Vo:l:"
    longopts = ["help", "config=", "timeout=", "verbosity=",
                "max-errors=", "color=", "valgrind", "output=", "log=", "list"]
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err:
        print(str(err))
        print(_(i18n.USAGE_en))
        sys.exit(2)
    opts = dict(opts)

    if '-h' in opts or '--help' in opts:
        print(_(i18n.USAGE_en))
        print()
        print(_(i18n.HELP_en))
        sys.exit(0)

    _list = False
    if '--list' in opts:
        _list = True

    if len(args) < 1 or (len(args) < 2 and not _list):
        print(_(i18n.USAGE_en))
        sys.exit(2)

    def optval(key1, key2, default=None, result_type=None):
        x = opts.get(key1, opts.get(key2, default))
        if result_type is None:
            return x
        try:
            return result_type(x)
        except ValueError:
            print(_("Invalid parameter ('%s')") % x)
            sys.exit(2)

    verbosity = optval('-v', '--verbosity', '3', int)
    if verbosity < 0 or verbosity > 4:
        print(_("Invalid parameter ('%d')") % verbosity)
        sys.exit(2)

    timeout = optval('-t', '--timeout', '10', float)
    if timeout < 0:
        print(_("Invalid parameter ('%f')") % timeout)
        sys.exit(2)

    maxerrors = optval('-m', '--max-errors', '4', int)
    if maxerrors < 1:
        print(_("Invalid parameter ('%d')") % maxerrors)
        sys.exit(2)

    config = optval('-c', '--config', '', str)

    color = optval('-C', '--color', 'AUTO', str).upper()
    if color not in ("YES", "NO", "AUTO"):
        print(_("Invalid parameter ('%s')") % color)
        sys.exit(2)
    color = (color == "YES" or (color == "AUTO" and sys.stdout.isatty()))

    output = optval('-o', '--output', 'resume', str).upper()
    if output not in ("RESUME", "JSON", "CSV"):
        print(_("Invalid parameter ('%s')") % output)
        sys.exit(2)

    logfile = optval('-l', '--log', _DEFAULT_LOG_FILE, str)
        
    valgrind = (True if '-V' in opts or '--valgrind' in opts else False)
    opts = dict(config=config, verbosity=verbosity, timeout=timeout,
                maxerrors=maxerrors, color=color, valgrind=valgrind,
                output=output, logfile=logfile, list=_list)

    return (args, opts)


def parse_file(filename):
    """Read the content of a file containing tests."""
    if filename == "":
        return []
    try:
        with open(filename, "rt") as f:
            return list(parser.parse_sections(f))
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


def test_names_list(test_suite):
    """Build a list containing all the test's names of a test suite."""
    test_names = []
    for test in test_suite.test_cases():
        test_names.append(test.description)
    return test_names


def print_test_names_list(test_suite):
    """Print a list containing all the test's names of a test suite."""
    test_names = test_names_list(test_suite)
    i = 1
    for test_name in test_names:
        try:
            print(str(i) + ')  ' + test_name)
        except TypeError:
            print(str(i) + ')   NoName')
        i += 1
    exit(0)


def main():
    """Setup the environment and starts the test session."""
    test_number = None
    (args, opts) = parse_options()

    cfg = parse_file(opts["config"])

    try:
        test_number = int(args[0]) - 1
        td = parse_file(args[1])
    except ValueError:
        td = parse_file(args[0])

    if opts['valgrind']:
        cfg.append(testdata.Section('VALGRIND', []))

    suite = testdata.TestSuite(cfg + td)

    if test_number is not None:
        try:
            if test_number < 0:
                raise IndexError
            suite = suite.test_cases()[test_number]
        except IndexError:
            print("\nTest number " + str(test_number + 1) + " doesn't exist.\n")
            print("Use the 'list' option to list all the available tests.\n")
            exit(2)

    execlass = (valgrind.ValgrindExecutor if opts["valgrind"]
                else executor.Executor)
    exe = execlass()

    if opts['list']:
        print_test_names_list(suite)

    if opts["output"] == "JSON":
        fmt = jsonformatter.JSONFormatter(indent=4)
    elif opts["output"] == "CSV":
        fmt = csvformatter.CSVFormatter()
    else:
        fmtclass = (formatter.ColoredTextFormatter if opts["color"]
                    else formatter.TextFormatter)
        fmt = fmtclass(verbosity=opts["verbosity"],
                       maxerrors=opts["maxerrors"])

    # Pvcheck returns as exit code the number of failed tests.
    # 255 represents a generic error.
    retcode = 255
    with open(opts["logfile"], "at") as logfile:
        logfmt = jsonformatter.JSONFormatter(logfile)
        combfmt = formatter.CombinedFormatter([fmt, logfmt])
        pvc = pvcheck.PvCheck(exe, combfmt)
        if test_number is None:
            failures = pvc.exec_suite(suite, args[1:],
                                      timeout=opts["timeout"])
        else:
            failures = pvc.exec_single_test(suite, args[2:],
                                            timeout=opts["timeout"])

        retcode = min(failures, 254)
        logfile.write("\n")
    sys.exit(retcode)

if __name__ == "__main__":
    main()
