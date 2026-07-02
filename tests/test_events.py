# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import os
import random
import string
import unittest
from pathlib import Path

from json_log_formatter import JSONFormatter

from bievents import (
    BI_BUSINESS_UNIT_UNKNOWN,
    BI_EVENT_STATUS_ERROR,
    BI_EVENT_STATUS_SUCCESS,
    BI_LOGGER_NAME,
    BiEventAbstract,
)

LOG_DIR = os.path.join(Path(__file__).resolve().parent.parent, "log")
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

formatter = JSONFormatter()
json_handler = logging.FileHandler(filename=os.path.join(LOG_DIR, "bievents-test-json.log"))
json_handler.setFormatter(formatter)
logger = logging.getLogger(BI_LOGGER_NAME)
logger.addHandler(json_handler)
logger.setLevel(logging.DEBUG)

TEST_ENVIRONMENT = "bi unit testing environment"
TEST_SOURCE = "bievents"


class TestException(Exception):
    # helper exception raised on purpose in scenarios, not a test class
    __test__ = False


class SimplestEvent(BiEventAbstract):
    details_type = "Simplest Test Event"
    version = 1


class SimpleEvent(BiEventAbstract):
    details_type = "Simple Test Event"
    version = 1

    def __init__(self, **kwargs):
        self.details = {"example_value": "Example text value"}
        super().__init__(**kwargs)


class SimpleOngoingEvent(BiEventAbstract):
    details_type = "Simple Ongoing Test Event"
    version = 1

    def __init__(self, **kwargs):
        self.details = {"example_value": "Example text value"}
        super().__init__(**kwargs)


class MustBeOngoingEvent(BiEventAbstract):
    details_type = "Must Be Ongoing Test Event"
    version = 1
    is_ongoing_event = True  # wymuszenie ustawienia is_ongoing_event

    def __init__(self, **kwargs):
        self.details = {"example_value": "Example text value MustBeOngoingEvent"}
        super().__init__(**kwargs)


class CanNotBeOngoingEvent(BiEventAbstract):
    details_type = "Can Not Be Ongoing Test Event"
    version = 1
    is_ongoing_event = False  # wymuszenie ustawienia is_ongoing_event

    def __init__(self, **kwargs):
        self.details = {"example_value": "Example text value CanNotBeOngoingEvent"}
        super().__init__(**kwargs)


class TestEvents(unittest.TestCase):
    def test_simplest(self):
        """Simplest event creation"""
        bev = SimplestEvent(source=TEST_SOURCE, business_unit=BI_BUSINESS_UNIT_UNKNOWN, environment=TEST_ENVIRONMENT)
        data = bev.get_event_data()
        self.assertFalse(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Simplest Test Event")
        self.assertEqual(data["event_source"], TEST_SOURCE)
        self.assertEqual(data["business_unit"], BI_BUSINESS_UNIT_UNKNOWN)
        self.assertEqual(data["environment"], TEST_ENVIRONMENT)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["time_duration"], 0)
        self.assertEqual(data["details"], {})

    def test_simple_with_success(self):
        """Simple event finished with success"""
        bev = SimpleEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            status=BI_EVENT_STATUS_SUCCESS,
            details={"value_in_init": "test123"},
            finish_tag="success finish tag",
            debug="SimpleEvent finished with success",
        )
        data = bev.get_event_data()
        self.assertFalse(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Simple Test Event")
        self.assertEqual(data["status"], "success")
        self.assertIn("details", data)
        self.assertIn("example_value", data["details"])
        self.assertIn("value_in_init", data["details"])
        self.assertEqual(data["details"]["example_value"], "Example text value")
        self.assertEqual(data["details"]["value_in_init"], "test123")

    def test_simple_with_error(self):
        """Simple event finished with error"""
        bev = SimpleEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            status=BI_EVENT_STATUS_ERROR,
            finish_tag="error finish tag",
            error_message="This is error because this is test with error",
            debug="SimpleEvent finished with error",
        )
        data = bev.get_event_data()
        self.assertFalse(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Simple Test Event")
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["finish_tag"], "error finish tag")
        self.assertEqual(data["error_message"], "This is error because this is test with error")
        self.assertEqual(data["debug"][0], "SimpleEvent finished with error")

    def test_simple_with_exception(self):
        """Simple event finished with error"""
        try:
            # exception must be raised to include "exception.__traceback__" data
            raise TestException("Raising intended exception for test")
        except Exception as e:
            bev = SimpleEvent(
                source=TEST_SOURCE,
                business_unit=BI_BUSINESS_UNIT_UNKNOWN,
                environment=TEST_ENVIRONMENT,
                exception=e,
                debug="SimpleEvent finished with exception",
            )
            data = bev.get_event_data()
            self.assertFalse(data["is_ongoing_event"])
            self.assertEqual(data["details_type"], "Simple Test Event")
            self.assertEqual(data["status"], "exception")
            self.assertEqual(data["error_message"], "Raising intended exception for test")
            self.assertEqual(data["exception_class"], "TestException")
            self.assertEqual(data["exception_traceback"][0][:9], "Traceback")
            self.assertEqual(data["debug"][0], "SimpleEvent finished with exception")

    def test_ongoing_with_success(self):
        """Testing event of ongoing type with success"""
        bev = SimpleOngoingEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            details={"value_in_init": "test123"},
            is_ongoing_event=True,
        )
        bev.set_detail("random_value", "".join(random.choices(string.ascii_uppercase + string.digits, k=16)))
        bev.debug("SimpleOngoingEvent finished with success")
        bev.finish_with_success(finish_tag="success finish tag")
        data = bev.get_event_data()
        self.assertTrue(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Simple Ongoing Test Event")
        self.assertEqual(data["status"], "success")
        self.assertIn("details", data)
        self.assertIn("example_value", data["details"])
        self.assertIn("value_in_init", data["details"])
        self.assertEqual(data["details"]["example_value"], "Example text value")
        self.assertEqual(data["details"]["value_in_init"], "test123")

    def test_ongoing_with_error(self):
        """Testing event of ongoing type with catched exception"""
        bev = SimpleOngoingEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            is_ongoing_event=True,
        )
        bev.set_detail("random_value", "".join(random.choices(string.ascii_uppercase + string.digits, k=16)))
        try:
            raise TestException("This Exception is intended")
        except Exception as e:
            bev.debug("SimpleOngoingEvent finished with error")
            bev.finish_with_error(finish_tag="error finish tag", error_message=str(e))
        data = bev.get_event_data()
        self.assertEqual(data["details_type"], "Simple Ongoing Test Event")
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["finish_tag"], "error finish tag")
        self.assertEqual(data["error_message"], "This Exception is intended")
        self.assertEqual(data["debug"][0], "SimpleOngoingEvent finished with error")

    def test_ongoing_with_exception(self):
        """Testing exception while ongoing event"""
        bev = SimpleOngoingEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            is_ongoing_event=True,
        )
        try:
            bev.set_detail("random_value", "".join(random.choices(string.ascii_uppercase + string.digits, k=10)))
            raise TestException("Raising intended exception for test")
        except Exception as e:
            bev.finish_with_exception(e, debug="SimpleOngoingEvent finished with exception")
        data = bev.get_event_data()
        self.assertEqual(data["details_type"], "Simple Ongoing Test Event")
        self.assertEqual(data["status"], "exception")
        self.assertEqual(data["error_message"], "Raising intended exception for test")
        self.assertEqual(data["exception_class"], "TestException")
        self.assertEqual(data["exception_traceback"][0][:9], "Traceback")
        self.assertEqual(data["debug"][0], "SimpleOngoingEvent finished with exception")

    def test_forced_is_ongoing(self):
        """Testing MustBeOngoingEvent event"""
        bev = MustBeOngoingEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            details={"value_in_init": "test123"},
        )
        bev.set_detail("random_value", "".join(random.choices(string.ascii_uppercase + string.digits, k=16)))
        bev.debug("SimpleOngoingEvent finished with success")
        bev.finish_with_success(finish_tag="success finish tag")
        data = bev.get_event_data()
        self.assertTrue(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Must Be Ongoing Test Event")
        self.assertEqual(data["status"], "success")
        self.assertIn("details", data)
        self.assertIn("example_value", data["details"])
        self.assertIn("value_in_init", data["details"])
        self.assertEqual(data["details"]["example_value"], "Example text value MustBeOngoingEvent")
        self.assertEqual(data["details"]["value_in_init"], "test123")

    def test_cannot_be_ongoing_event(self):
        """Testing CanNotBeOngoingEvent event"""
        bev = CanNotBeOngoingEvent(
            source=TEST_SOURCE,
            business_unit=BI_BUSINESS_UNIT_UNKNOWN,
            environment=TEST_ENVIRONMENT,
            status=BI_EVENT_STATUS_SUCCESS,
            details={"value_in_init": "test123"},
            finish_tag="success finish tag",
            debug="SimpleEvent finished with success",
        )
        data = bev.get_event_data()
        self.assertFalse(data["is_ongoing_event"])
        self.assertEqual(data["details_type"], "Can Not Be Ongoing Test Event")
        self.assertEqual(data["status"], "success")
        self.assertIn("details", data)
        self.assertIn("example_value", data["details"])
        self.assertIn("value_in_init", data["details"])
        self.assertEqual(data["details"]["example_value"], "Example text value CanNotBeOngoingEvent")
        self.assertEqual(data["details"]["value_in_init"], "test123")

    def test_forced_cannot_be_ongoing(self):
        """Testing CanNotBeOngoingEvent event can not be set to ongoing"""

        def improper_usage():
            CanNotBeOngoingEvent(
                source=TEST_SOURCE,
                business_unit=BI_BUSINESS_UNIT_UNKNOWN,
                environment=TEST_ENVIRONMENT,
                status=BI_EVENT_STATUS_SUCCESS,
                details={"value_in_init": "test123"},
                finish_tag="success finish tag",
                debug="SimpleEvent finished with success",
                is_ongoing_event=True,
            )

        self.assertRaises(Exception, improper_usage)


if __name__ == "__main__":
    unittest.main()
