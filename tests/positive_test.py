from samltest import SamlTest


class PositiveTest(SamlTest):
    """Sends the unmodifed token to the SP to verify the setup is working.
    """

    expect_success = True

    def mutate_response(self):
        pass # don't mutate the tree at all

