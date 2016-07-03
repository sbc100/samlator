import base64
import os
import requests

from lxml import etree

OUT_DIR = 'out'


def reformat_xml(xml):
    root = etree.fromstring(xml)
    return etree.tostring(root, pretty_print=True)


class Error(Exception):
    pass


class SamlTest(object):
    """Base class for SAML tests"""
    expect_success = False
    namespaces = {
        'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        'ds': 'http://www.w3.org/2000/09/xmldsig#'
    }

    def __init__(self, acs_url, valid_token):
        self.acs_url = acs_url
        self.valid_token = valid_token
        self.token_root = etree.fromstring(self.valid_token)

    def get_output_dir(self):
        dirname = os.path.join(OUT_DIR, self.__class__.__name__)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return dirname

    def assert_equal(self, actual, expected, message=None):
        if expected != actual:
            raise Error('%s. Expected %s but got %s' % (message, expected, actual))

    def assert_not_equal(self, actual, expected, message=None):
        if expected == actual:
            raise Error('%s. %s' % (message, actual))

    def write_file(self, name, content):
        with open(os.path.join(self.get_output_dir(), name), 'w') as f:
            f.write(content)

    def run(self):
        self.write_file('orig', self.valid_token)

        self.mutate_response()

        new_token = etree.tostring(self.token_root)
        self.write_file('modified', new_token)

        self.write_file('formatted_orig', reformat_xml(self.valid_token))
        self.write_file('formatted_modified', reformat_xml(new_token))

        resp = base64.b64encode(new_token)
        res = requests.post(self.acs_url, data={'SAMLResponse': resp})
        self.handle_sp_response(res)

    def handle_sp_response(self, response):
        if self.expect_success:
            self.assert_equal(response.status_code, 200,
                'Server did not accept valid token')
        else:
            self.assert_not_equal(response.status_code, 200,
                'Server accepted the invalid token')

    def xpath(self, query):
        return self.token_root.xpath(query, namespaces=self.namespaces)
