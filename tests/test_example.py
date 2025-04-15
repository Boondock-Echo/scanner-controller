"""
This module contains example test cases for pytest.

The purpose of this module is to demonstrate how to write and run tests
using pytest.
"""


def test_sample():
    """
    Test that 1 + 1 equals 2.

    Just adding this to test that test is testing tests :)
    """
    assert 1 + 1 == 2


def test_string_concatenation():
    """
    Test that string concatenation works as expected.

    In this case, we concatenate two string literals and check if the result
    is as expected.
    """
    assert "Hello, " + "World!" == "Hello, World!"


def test_list_append():
    """
    Test that appending to a list works correctly.

    In this case, we create a list, append an element to it, and check if the
    result is as expected.
    """
    my_list = [1, 2, 3]
    my_list.append(4)
    assert my_list == [1, 2, 3, 4]


def test_dictionary_access():
    """
    Test that accessing dictionary values works as expected.

    Testing dictionary access by creating a dictionary and checking if we can
    access its values correctly.
    """
    my_dict = {"key": "value"}
    assert my_dict["key"] == "value"
