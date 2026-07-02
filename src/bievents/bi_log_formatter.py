# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json_log_formatter


class BiFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        return extra
