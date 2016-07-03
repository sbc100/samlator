from samltest import SamlTest


class StripSignature(SamlTest):
    """Removes the XML signature from the SAML assertion.
    """

    def mutate_response(self):
        # Find the `Signature` element
        signatures = self.xpath('//samlp:Response/saml:Assertion/ds:Signature')
        self.assert_equal(len(signatures), 1, 'expected a single signature')

        # Remove the `Signature` element from the tree
        sig = signatures[0]
        sig.getparent().remove(sig)

