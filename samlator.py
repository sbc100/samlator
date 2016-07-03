#!/usr/bin/env python
"""Test suite for SAML service providers
"""
import argparse
import base64
import json
import lxml.html
import lxml.etree
import requests
import sys
import tests
import textwrap
import traceback

from onelogin.saml2.auth import OneLogin_Saml2_Authn_Request
from onelogin.saml2.auth import OneLogin_Saml2_Response
from onelogin.saml2.auth import OneLogin_Saml2_Settings
from onelogin.saml2.auth import OneLogin_Saml2_Utils


SETTINGS_FILE = 'config/settings.json'
DEBUG = False


class Error(Exception):
    pass


def message(msg):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()


def trace(msg):
    if DEBUG:
        message(msg)


class TestHarness(object):
    def __init__(self):
        self.fail_count = 0
        self.test_count = 0

        with open(SETTINGS_FILE) as f:
            settings_data = json.load(f)

        self.settings = OneLogin_Saml2_Settings(settings_data)
        self.acs_url = self.settings.get_sp_data()['assertionConsumerService']['url']
        self.sso_url = self.settings.get_idp_data()['singleSignOnService']['url']

    def request_token_from_idp(self):
        authn = OneLogin_Saml2_Authn_Request(self.settings)
        sso_url = self.settings.get_idp_data()['singleSignOnService']['url']
        trace('Requesting token from: %s' % sso_url)

        # Generate a request URL
        params = { 'BypassAuth': '1', 'SAMLRequest': authn.get_request() }
        res = requests.get(sso_url, params=params)
        res.raise_for_status()

        # Read HTML response
        root = lxml.html.fromstring(res.text)

        # Find SAMLResponse value withing returned form
        samlresponse = root.xpath("//input[@id='SAMLResponse']/@value")[0]

        response = OneLogin_Saml2_Response(self.settings, samlresponse)
        response.check_status()

        return response.response

    def run_test(self, klass):
        try:
            token = self.request_token_from_idp()
        except requests.exceptions.RequestException as e:
            message('[ FAILED  ] %s' % message('error getting token from IdP: %s' % str(e)))
            return 1

        try:
            message('[ RUN     ] %s' % klass.__name__)
            klass(self.acs_url, token).run()
            message('[ SUCCESS ]')
            return 0
        except Exception as e:
            traceback.print_exc()
            message('[ FAILED  ] %s' % klass.__name__)
            return 1

    def list_tests(self):
        for i, test in enumerate(tests.all_tests):
            if i != 0:
                message('')
            message(test.__name__)
            message('-' * len(test.__name__))
            message('')
            message(test.__doc__.strip())

    def run_tests(self, named_tests):
        if named_tests:
            test_list = []
            for name in named_tests:
                test_class = getattr(tests, name, None)
                if not test_class:
                    raise Error('Unknown test: %s' % name)
                test_list.append(test_class)
        else:
            test_list = tests.all_tests

        message('Running SAML tests')
        message('SP : %s' % self.acs_url)
        message('IdP: %s' % self.sso_url)


        for klass in test_list:
            self.test_count += 1
            if self.run_test(klass):
                self.fail_count += 1
                if klass == tests.PositiveTest:
                    message('Positive test failed, aborting test run')
                    break

        message('')

        if self.fail_count:
            message('%s/%s tests failed.' % (self.fail_count, self.test_count))
            return 1

        message('%s tests passed.' % (self.test_count))
        return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='list tests')
    parser.add_argument('tests', metavar='TEST', type=str, nargs='*',
                        help='names of tests to run')
    args = parser.parse_args(argv)

    harness = TestHarness()
    if args.list:
        return harness.list_tests()
    else:
        return harness.run_tests(args.tests)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Error as e:
        sys.stderr.write('samlator: %s\n' % str(e))
        sys.exit(1)
