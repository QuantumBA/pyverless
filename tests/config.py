import json

from neomodel import db, clear_neo4j_database
# from neomodel import install_all_labels  # Comment / Uncomment as needed


def _(response):
    """
    Given a handler response, return the status_code and data. This is ment
    to make the code more readable
    """
    data = json.loads(response['body'])
    status_code = response['statusCode']

    return data, status_code


class Neo4jTestCase():

    def setup_class(self):
        # clear_neo4j_database(db)  # Comment / Uncomment as needed
        # install_all_labels()  # Comment / Uncomment as needed
        pass

    def teardown_class(self):
        clear_neo4j_database(db)
