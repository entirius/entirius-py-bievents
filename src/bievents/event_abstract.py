# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import inspect
import logging
import socket
import sys
import traceback
import uuid
from typing import Any

# name of bi json logger
BI_LOGGER_NAME = "business_intelligence"

# Value set to business_unit field when it is unknown
BI_BUSINESS_UNIT_UNKNOWN = "unknown"

# const for event "status"
BI_EVENT_STATUS_SUCCESS = "success"
BI_EVENT_STATUS_ERROR = "error"
BI_EVENT_STATUS_EXCEPTION = "exception"

MAX_ERROR_MESSAGE_LENGTH = 256


#   {
#     "time_start": "2021-08-20 11:36:11.769",
#     "time_end": "2021-08-20 11:36:11.769",
#     "status": "success",
#     "details_type": "Products Export To Magento End Session",
#     "details": {
#       "shop": "example_shop",
#       "magento_url": "https://magento.example.com/",
#       "magento_stores": [
#         "store_en"
#       ],
#       "duration_of_import_secs": 29
#     },
#     "version": 0,
#     "id": "3272a1fa-294e-48b8-943c-46a2d1345559",
#     "source": "integrations.magento_2",
#     "business_unit": "example-unit",
#     "environment": "dev",
#     "resources": [
#       "example-resource"
#     ],
#     "is_ongoing_event": false
#   }
#
#   {
#     ...
#     "status": "error",
#     "finish_tag": "xxxxx",
#     "error_message": "xxxxx",
#   }
#
#   {
#     ...
#     "status": "exception",
#     "error_message": "xxxxx",
#     "exception_traceback": "xxxxx",
#     "exception_class": "KeyboardInterrupt",
#   }


class BiEventAbstract:
    version = 2  # increase version number on BiEvents version dump
    details_type = None  # must be inherited

    def __init__(
        self,
        source: str,
        business_unit: str,
        environment: str,
        status: str | None = None,
        details: dict | None = None,
        is_ongoing_event: bool | None = None,
        finish_tag: str | None = None,  # if is_ongoing_event = False
        error_message: str | None = None,  # if status = error
        exception: BaseException | None = None,
        debug: str | None = None,
        **kwargs,  # all other kargs are set to event details
    ):
        if hasattr(self, "details"):
            self.details = dict(self.details)
        else:
            self.details = {}
        if details:
            self.details.update(dict(details))
        self.finish_tag = None
        self.error_message = None
        self.exception = None
        self.debug_logs = []
        self.__event = None  # event object that is serialized to logger
        if not self.details_type:
            raise Exception("details_type must be set")
        self._is_finished = False
        self.bi_logger = logging.getLogger(BI_LOGGER_NAME)
        if hasattr(self, "is_ongoing_event"):
            # forced is_ongoing_event setting
            self.is_ongoing_event = bool(self.is_ongoing_event)
            if is_ongoing_event is not None:
                if self.is_ongoing_event != bool(is_ongoing_event):
                    raise Exception(
                        f'Event "{self.__class__.__name__}" is forced to be is_ongoing_event={self.is_ongoing_event}, this can not be changed'
                    )
        else:
            self.is_ongoing_event = False if is_ongoing_event is None else bool(is_ongoing_event)
        self.time_start = datetime.datetime.now(datetime.UTC)
        self.id = str(uuid.uuid4())
        if source is None:
            raise Exception("BiEvent source must be set")
        else:
            self.source = str(source).lower()
        if business_unit is None:
            self.business_unit = BI_BUSINESS_UNIT_UNKNOWN
        else:
            self.business_unit = str(business_unit).lower()
        if environment is None:
            raise Exception("BiEvent environment must be set")
        else:
            self.environment = str(environment).lower()
        self.resources = [socket.gethostname()]
        if kwargs:
            self.set_initial_kwargs(kwargs)
        self.set_finish_tag(finish_tag)
        self.set_error_message(error_message)
        self.debug(debug)
        if exception is not None:
            self.finish_with_exception(exception)
            return
        if self.is_ongoing_event:
            assert status is None, "Status can not be set for ongoing events"
            self.status = None
        else:
            self.status = None if status is None else str(status)
            self.finish()

    def get_event_version(self):
        """Full Event version is created from version strings of all its parents"""
        class_list = list(inspect.getmro(self.__class__))
        class_list.reverse()
        del class_list[0]  # "object"
        sub_versions = []
        for c in class_list:
            sub_versions.append(str(c.version))
        return "-".join(sub_versions)

    def debug(self, debug: str):
        if not debug:
            return
        if isinstance(debug, BaseException):
            self.exception = debug
            return self.finish()
        msg = str(debug)
        self.debug_logs.append(msg)

    def set_detail(self, key: str, value: Any, group: str | None = None):
        assert self.is_ongoing_event, "Can not set_detail() for NOT ONGOING events"
        if group:
            if group not in self.details:
                self.details[group] = {}
            self.details[group][key] = value
        else:
            self.details[key] = value

    def set_details(self, details: dict, group: str | None = None):
        assert self.is_ongoing_event, "You can use set_detail() only for ONGOING events, json is already dumped"
        if group:
            if group not in self.details:
                self.details[group] = {}
            for key, value in details.items():
                self.details[group][key] = value
        else:
            for key, value in details.items():
                self.details[key] = value

    def set_initial_kwargs(self, kwargs):
        for key, value in kwargs.items():
            self.details[key] = value

    def set_finish_tag(self, finish_tag: str | None = None):
        if not finish_tag:
            return
        self.finish_tag = str(finish_tag)[:128]

    def set_error_message(self, error_message: str | None = None):
        if not error_message:
            return
        self.error_message = str(error_message)[:MAX_ERROR_MESSAGE_LENGTH]

    def finish_with_success(self, finish_tag: str | None = None, details: dict | None = None, debug=None):
        """Should be used when business process raised an exception,
        but it is caught, and has been handled
        """
        if details:
            self.set_details(details=details)
        self.status = BI_EVENT_STATUS_SUCCESS
        self.set_finish_tag(finish_tag)
        self.finish(debug=debug)

    def finish_with_error(
        self,
        finish_tag: str | None = None,
        error_message: str | None = None,
        details: dict | None = None,
        debug=None,
    ):
        """Should be used when business process raised an exception,
        but it is caught, and has been handled
        """
        if details:
            self.set_details(details=details)
        self.status = BI_EVENT_STATUS_ERROR
        self.set_finish_tag(finish_tag)
        self.set_error_message(error_message)
        self.finish(debug=debug)

    def finish_with_exception(self, e: BaseException, details: dict | None = None, debug=None):
        """Should be used when business process raised an exception,
        and we don't knot how it should be handled
        """
        if details:
            self.set_details(details=details)
        self.status = BI_EVENT_STATUS_EXCEPTION
        self.exception = e
        self.finish(debug=debug)

    def get_event_data(self):
        return self.__event

    def finish(self, debug=None):
        assert not self._is_finished, f"Event {self} is already finished"
        if debug is not None:
            self.debug(debug)
        if self.exception is not None:
            self.status = BI_EVENT_STATUS_EXCEPTION
        else:
            if self.status is None:
                self.status = BI_EVENT_STATUS_SUCCESS
        if self.is_ongoing_event:
            self.time_end = datetime.datetime.now(datetime.UTC)
            self.time_duration = (self.time_end - self.time_start) / datetime.timedelta(milliseconds=1)
        else:
            self.time_end = self.time_start
            self.time_duration = 0
        self.__event = {
            "details_type": self.details_type,
            "event_source": self.source,
            "business_unit": self.business_unit,
            "environment": self.environment,
            "id": self.id,
            "version": self.get_event_version(),
            "status": self.status,
            "resources": self.resources,
            "is_ongoing_event": self.is_ongoing_event,
            "time_start": self.time_start.isoformat(),
            "time_end": self.time_end.isoformat(),
            "time_duration": self.time_duration,
            "details": self.details,
        }
        if self.finish_tag:
            self.__event["finish_tag"] = self.finish_tag
        if self.error_message:
            self.__event["error_message"] = self.error_message
        if self.debug_logs:
            self.__event["debug"] = self.debug_logs
        if self.exception:
            self.__event["error_message"] = str(self.exception)[:MAX_ERROR_MESSAGE_LENGTH]
            self.__event["exception_class"] = self.exception.__class__.__name__
            self.__event["exception_traceback"] = list(
                traceback.format_exception(type(self.exception), value=self.exception, tb=self.exception.__traceback__)
            )
        self.bi_logger.info(self.details_type, extra=self.__event)
        self._is_finished = True


#
# BI Abstract Event representing Celery tasks
#
class BiCeleryTaskEventAbstract(BiEventAbstract):
    def __init__(self, stop_process: bool | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if stop_process is not None:
            self.details["stop_process"] = stop_process

    def celery_subtask_created(self, subtask_name: str, is_already_in_queue: bool = False, increase: int = 1):
        subtask_name = subtask_name.lower()
        if "celery_subtasks" not in self.details:
            self.details["celery_subtasks"] = {}
        if subtask_name not in self.details["celery_subtasks"]:
            self.details["celery_subtasks"][subtask_name] = {"created": 0, "already_in_queue": 0}
        if is_already_in_queue:
            self.details["celery_subtasks"][subtask_name]["already_in_queue"] += increase
        else:
            self.details["celery_subtasks"][subtask_name]["created"] += increase

    def increase_request_counter(self, system_name: str, increase: int = 1):
        system_name = system_name.lower()
        if "requests_done" not in self.details:
            self.details["requests_done"] = {}
        if system_name not in self.details["requests_done"]:
            self.details["requests_done"][system_name] = increase
        else:
            self.details["requests_done"][system_name] += increase

    def set_document_status(self, document_name: str, is_created: bool):
        if "documents_status" not in self.details:
            self.details["documents_status"] = {}
        self.details["documents_status"][document_name] = "created" if is_created else "updated"


#
# Handling Django Commands
#
class DjangoCommandHasBeenExecutedEvent(BiEventAbstract):
    details_type = "Django Command Has Been Executed"
    version = 1

    def __init__(self, command_name: str, options: dict = None, **kwargs):
        super().__init__(**kwargs)
        # upewniam sie, ze dzialam na kopii
        options_clone = {}
        if options is not None:
            options_clone = options.copy()
            self.cleanup_options(options_clone)
        self.details = {"command_name": command_name, "options": dict(options_clone)}

    def cleanup_options(self, options: dict):
        """Removes typical Django options that are not interesting"""
        for k in ["verbosity", "pythonpath", "no_color", "force_color", "skip_checks", "traceback", "settings"]:
            if k in options:
                del options[k]


def bi_django_command_decorator(func):
    def wrapper(*args, **options):
        from django.conf import settings

        command_name = sys.argv[1]
        bie = DjangoCommandHasBeenExecutedEvent(
            source="bievents",
            business_unit=settings.BI_BUSINESS_UNIT,
            environment=settings.BI_ENVIRONMENT,
            command_name=command_name,
            options=options,
            is_ongoing_event=True,
        )
        self_command = args[0]
        try:
            func(*args, **options)
            finish_tag = "Command finished with success"
            bie.finish_with_success(finish_tag=finish_tag)
            self_command.stdout.write(self_command.style.SUCCESS(finish_tag))
        except ValueError as e:
            bie.finish_with_exception(e)
            self_command.stdout.write(self_command.style.ERROR(f"Invalid parameters: {e}"))
        except KeyboardInterrupt:
            bie.finish_with_error(finish_tag="Keyboard Interrupt")
            self_command.stdout.write(self_command.style.ERROR("\nKeyboard Interrupt"))
        except BaseException as e:
            bie.finish_with_exception(e)
            self_command.stdout.write(self_command.style.ERROR(f"Exception: {e}"))
            raise e

    return wrapper
