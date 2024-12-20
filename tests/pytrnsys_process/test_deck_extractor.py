import json

from pytrnsys_process import utils
from pytrnsys_process.deck import parser, extractor
from tests.pytrnsys_process import constants as const


def test_get_direct_constants():
    file_content = utils.get_file_content_as_string(
        const.DATA_FOLDER / "deck/complete-0-SnkScale0.6000-StoreScale5.dck"
    )

    tree = parser.parse_dck(file_content)
    visitor = extractor.ConstantsVisitor()
    visitor.visit(tree)
    expected_json_file = const.DATA_FOLDER / "deck/expected_constants.json"

    expected_dict = json.loads(
        utils.get_file_content_as_string(expected_json_file)
    )

    assert expected_dict == visitor.resolved_constants
