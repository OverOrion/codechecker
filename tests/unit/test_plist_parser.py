# -----------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -----------------------------------------------------------------------------

"""
Test the parsing of the plist generated by multiple clang versions.

With the newer clang releases more information is available in the plist files.

* Before Clang v3.7:
  - Not supported

* Clang v3.7:
  - Checker name is available in the plist
  - Report hash is not avilable (generated based on the report path elements
    see report handling and plist parsing modules for more details

* After Clang v3.8:
  - Checker name is available
  - Report hash is available

"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import unittest

from libcodechecker import plist_parser

# These are the base skeletons for the main report sections where the
# report hash and checker name is missing.
# Before comparison in the tests needs to be extended.
div_zero_skel = \
    {'category': 'Logic error',
     'issue_context': 'generate_id',
     'issue_context_kind': 'function',
     'description': 'Division by zero',
     'type': 'Division by zero',
     'issue_hash': '1',
     'location': {
         'line': 7,
         'col': 14,
         'file': 1
         }
     }

stack_addr_skel = \
    {'category': 'Logic error',
     'issue_context': 'test',
     'issue_context_kind': 'function',
     'description': "Address of stack memory associated with local variable"
                    " 'str' is still referred to by the global variable 'p'"
                    " upon returning to the caller."
                    "  This will be a dangling reference",
     'type': 'Stack address stored into global variable',
     'issue_hash': '3',
     'location': {
         'line': 16,
         'col': 1,
         'file': 0
         }
     }

# Base skeletons for reports where the checker name is already available.
div_zero_skel_name = \
    {'category': 'Logic error',
     'issue_context': 'generate_id',
     'issue_context_kind': 'function',
     'description': 'Division by zero',
     'check_name': 'core.DivideZero',
     'type': 'Division by zero',
     'issue_hash': '1',
     'location': {
         'line': 7,
         'col': 14,
         'file': 1
         }
     }

stack_addr_skel_name = \
    {'category': 'Logic error',
     'issue_context': 'test',
     'issue_context_kind': 'function',
     'description': "Address of stack memory associated with local variable"
                    " 'str' is still referred to by the global variable 'p'"
                    " upon returning to the caller."
                    "  This will be a dangling reference",
     'check_name': 'core.StackAddressEscape',
     'type': 'Stack address stored into global variable',
     'issue_hash': '3',
     'location': {
         'line': 16,
         'col': 1,
         'file': 0
         }
     }

# Main sections for reports where checker name and report hash is available.
div_zero_skel_name_hash = \
    {'category': 'Logic error',
     'check_name': 'core.DivideZero',
     'description': 'Division by zero',
     'issue_context': 'generate_id',
     'issue_context_kind': 'function',
     'issue_hash_content_of_line_in_context':
         '79e31a6ba028f0b7d9779faf4a6cb9cf',
     'issue_hash_function_offset': '1',
     'location': {
         'col': 14,
         'file': 1,
         'line': 7
         },
     'type': 'Division by zero'
     }

stack_addr_skel_name_hash = \
    {'category': 'Logic error',
     'issue_context': 'test',
     'issue_context_kind': 'function',
     'description': "Address of stack memory associated with local variable"
                    " 'str' is still referred to by the global variable 'p'"
                    " upon returning to the caller."
                    "  This will be a dangling reference",
     'check_name': 'core.StackAddressEscape',
     'type': 'Stack address stored into global variable',
     'issue_hash_content_of_line_in_context':
     'f7b5072d428e890f2d309217f3ead16f',
     'issue_hash_function_offset': '3',
     'location': {
         'line': 16,
         'col': 1,
         'file': 0
         }
     }


# core.StackAddressEscape hash generated by clang is different
# from the hash generated by the previous clang release.
stack_addr_skel_name_hash_after_v40 = \
    {'category': 'Logic error',
     'issue_context': 'test',
     'issue_context_kind': 'function',
     'description': "Address of stack memory associated with local variable"
                    " 'str' is still referred to by the global variable 'p'"
                    " upon returning to the caller."
                    "  This will be a dangling reference",
     'check_name': 'core.StackAddressEscape',
     'type': 'Stack address stored into global variable',
     'issue_hash_content_of_line_in_context':
     'a6d3464f8aab9eb31a8ea7e167e84322',
     'issue_hash_function_offset': '3',
     'location': {
         'line': 16,
         'col': 1,
         'file': 0
         }
     }


class PlistParserTestCaseNose(unittest.TestCase):
    """Test the parsing of the plist generated by multiple clang versions."""

    @classmethod
    def setup_class(cls):
        """Initialize test source file."""
        # Bugs found by these checkers in the test source files.
        cls.__found_checker_names = [
            'core.DivideZero',
            'core.StackAddressEscape',
            'deadcode.DeadStores']

        # Reports were found in these test files.
        cls.__found_file_names = ['test.cpp', './test.h']

        # Already generated plist files for the tests.
        cls.__this_dir = os.path.dirname(__file__)
        cls.__plist_test_files = os.path.join(
            cls.__this_dir, 'plist_test_files')

    def missing_checker_name_and_hash(self, reports):
        """
        The checker name and the report hash is generated
        by CodeChecker.
        """
        for report in reports:
            # Get the checker name detected by CodeChecker based
            # on the report description.
            checker_name = report.main['check_name']

            if checker_name == 'core.DivideZero':
                test_data = div_zero_skel
                # Report hash generated by CodeChecker.
                test_data['issue_hash_content_of_line_in_context'] = \
                    'e9fb5a280e64610cfa82472117c8d0ac'
                test_data['check_name'] = 'core.DivideZero'
                self.assertEqual(report.main, test_data)

            if checker_name == 'NOT FOUND':
                test_data = stack_addr_skel
                # Report hash generated by CodeChecker.
                test_data['issue_hash_content_of_line_in_context'] = \
                    'b1bc0e8364a255659522055d1e15cd16'
                test_data['check_name'] = 'NOT FOUND'
                self.assertEqual(report.main, test_data)

    def missing_hash(self, reports):
        """
        Checker name is available but report hash is not available
        yet in the generated plist.
        """

        for report in reports:
            checker_name = report.main['check_name']
            # Checker name should be available for all the reports.
            self.assertNotEquals(checker_name, 'NOT FOUND')

            if checker_name == 'core.DivideZero':
                test_data = div_zero_skel_name
                # Report hash generated by CodeChecker.
                test_data['issue_hash_content_of_line_in_context'] = \
                    'e9fb5a280e64610cfa82472117c8d0ac'
                self.assertEqual(report.main, test_data)

            if checker_name == 'core.StackAddressEscape':
                test_data = stack_addr_skel_name
                # core.StackAddressEscape hash is changed because the checker
                # name is available and it is included in the hash.
                test_data['issue_hash_content_of_line_in_context'] = \
                    'fafcb913bc0af67a55b130a7e8907fd2'
                self.assertEqual(report.main, test_data)

    def test_empty_file(self):
        """Plist file is empty."""
        empty_plist = os.path.join(self.__plist_test_files, 'empty_file')
        files, reports = plist_parser.parse_plist(empty_plist, None, False)
        self.assertEquals(files, [])
        self.assertEquals(reports, [])

    def test_no_bug_file(self):
        """There was no bug in the checked file."""
        no_bug_plist = os.path.join(
            self.__plist_test_files, 'clang-3.7-noerror.plist')
        files, reports = plist_parser.parse_plist(no_bug_plist, None, False)
        self.assertEquals(files, [])
        self.assertEquals(reports, [])

    def test_clang37_plist(self):
        """
        Check plist generated by clang 3.7 checker name should be in the plist
        file generating a report hash is still needed.
        """
        clang37_plist = os.path.join(
            self.__plist_test_files, 'clang-3.7.plist')
        files, reports = plist_parser.parse_plist(clang37_plist, None, False)

        self.assertEquals(files, self.__found_file_names)
        self.assertEquals(len(reports), 3)

        self.missing_hash(reports)

    def test_clang38_trunk_plist(self):
        """
        Check plist generated by clang 3.8 trunk checker name and report hash
        should be in the plist file.
        """
        clang38_plist = os.path.join(
            self.__plist_test_files, 'clang-3.8-trunk.plist')
        files, reports = plist_parser.parse_plist(clang38_plist, None, False)

        self.assertEquals(files, self.__found_file_names)
        self.assertEquals(len(reports), 3)

        valid_checker_names = []
        valid_checker_names.extend(self.__found_checker_names)

        for report in reports:
            checker_name = report.main['check_name']
            self.assertIn(checker_name, valid_checker_names)

            if checker_name == 'core.DivideZero':
                # Test data is still valid for this version.
                self.assertEqual(report.main,
                                 div_zero_skel_name_hash)

            if checker_name == 'core.StackAddressEscape':
                self.assertEqual(report.main,
                                 stack_addr_skel_name_hash)

    def test_clang40_plist(self):
        """
        Check plist generated by clang 4.0 checker name and report hash
        should be in the plist file.
        """
        clang40_plist = os.path.join(
            self.__plist_test_files, 'clang-4.0.plist')
        files, reports = plist_parser.parse_plist(clang40_plist, None, False)

        self.assertEquals(files, self.__found_file_names)
        self.assertEquals(len(reports), 3)

        valid_checker_names = []
        valid_checker_names.extend(self.__found_checker_names)

        for report in reports:
            checker_name = report.main['check_name']
            # Checker name should be in the plist file.
            self.assertNotEqual(checker_name, 'NOT FOUND')
            self.assertIn(checker_name, valid_checker_names)

            if checker_name == 'core.DivideZero':
                # Test data is still valid for this version.
                self.assertEqual(report.main,
                                 div_zero_skel_name_hash)

            if checker_name == 'core.StackAddressEscape':
                self.assertEqual(report.main,
                                 stack_addr_skel_name_hash_after_v40)

    def test_clang50_trunk_plist(self):
        """
        Check plist generated by clang 5.0 trunk checker name and report hash
        should be in the plist file.
        """
        clang50_trunk_plist = os.path.join(
            self.__plist_test_files, 'clang-5.0-trunk.plist')
        files, reports = plist_parser.parse_plist(clang50_trunk_plist, None,
                                                  False)
        self.assertEquals(files, self.__found_file_names)
        self.assertEquals(len(reports), 3)

        valid_checker_names = []
        valid_checker_names.extend(self.__found_checker_names)

        for report in reports:
            checker_name = report.main['check_name']
            # Checker name should be in the plist file.
            self.assertNotEqual(checker_name, 'NOT FOUND')
            self.assertIn(checker_name, valid_checker_names)

            if checker_name == 'core.DivideZero':
                # Test data is still valid for this version.
                self.assertEqual(report.main,
                                 div_zero_skel_name_hash)

            if checker_name == 'core.StackAddressEscape':
                self.assertEqual(report.main,
                                 stack_addr_skel_name_hash_after_v40)
