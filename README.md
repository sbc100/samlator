SAMLator - Black-box test suite for SAML SPs
============================================

[![Build Status](https://travis-ci.org/sbc100/samlator.svg?branch=master)](https://travis-ci.org/sbc100/samlator)

SAMLator is stand-alone black-box test suite that can be used to continuously
test SAML service providers known vulnerabilities and configuration errors.

See [tests.md](docs/tests.md) for details of the currently implemented tests.

**Note: This is pre-alpha proof of concept.**

## How it works

1. You give SAMLator a backdoor to your IdP which it can use to to generate
   valid tokens
2. SAMLator performs a positive test to verify your SP accepts valid tokens.
3. SAMLator runs a suite of tests based on mutating valid tokens in various
   ways.  If the SP accepts any of these invalid tokens then the test fails.

The suggested setup is to run the tests suite locally (either during
development in a CI system) against a local copy of your SP and IdP.
In this mode the entire test suite can be run offline, which increases
performance and minimizes flakiness.

## Setup

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

## Contributing

Contributing new test to SAMLator is fairly straight forward.  Most tests
involve mutating a SAML token progamatically.

### Testing the test

Each test in SAMLator must itself be tested.  Testing of the tests is done by
by creating a temporary SP which is monkey patched such that it exhibits
the bug in question.  We then verify that the patched SP fails under a given
SAMLator test, whereas the unpached SP passes.

## Similar Products

### SSOCheck - http://www.ssocircle.com/en/portfolio/ssocheck/tool-overview/

GUI (or API) driven black-box SAML testing tool.  As far as I can tell, the
tests suite is closed source.  Since the tests live behind an API they
cannot be run locally or offline.

### saml2test - https://github.com/rohe/saml2test

Black-box tests suite written in python and utilizing pysaml2 (
https://github.com/rohe/pysaml2).  So far I have not been unable to get
this to run, but combining efforts might make sense in the future.
