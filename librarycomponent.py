# Copyright 2008-2011 Nokia Networks
# Copyright 2011-2016 Ryan Tomac, Ed Manlove and contributors
# Copyright 2016-     Robot Framework Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from SeleniumLibrary.utils import is_noney, timestr_to_secs

from .context import ContextAware
import sys
#from .robotlibcore import PY2

PY2 = sys.version_info < (3,)

class LibraryComponent(ContextAware):

    def info(self, msg, html=False):
        logger.info(msg, html)

    def debug(self, msg, html=False):
        logger.debug(msg, html)

    def log(self, msg, level='INFO', html=False):
        if not is_noney(level):
            logger.write(msg, level.upper(), html)

    def warn(self, msg, html=False):
        logger.warn(msg, html)

    def log_source(self, loglevel='INFO'):
        self.ctx.log_source(loglevel)

    def assert_page_contains(self, locator, tag=None, message=None,
                             loglevel='TRACE'):
        if not self.find_element(locator, tag, required=False):
            self.log_source(loglevel)
            if is_noney(message):
                message = ("Page should have contained %s '%s' but did not."
                           % (tag or 'element', locator))
            raise AssertionError(message)
        logger.info("Current page contains %s '%s'."
                    % (tag or 'element', locator))

    def assert_page_not_contains(self, locator, tag=None, message=None,
                                 loglevel='TRACE'):
        if self.find_element(locator, tag, required=False):
            self.log_source(loglevel)
            if is_noney(message):
                message = ("Page should not have contained %s '%s'."
                           % (tag or 'element', locator))
            raise AssertionError(message)
        logger.info("Current page does not contain %s '%s'."
                    % (tag or 'element', locator))

    def get_timeout(self, timeout=None):
        if is_noney(timeout):
            return self.ctx.timeout
        return timestr_to_secs(timeout)

    def highlight_element(self, locator):
        elements = self.find_elements(locator)
        self._style=dict()
        if not elements:
            raise ElementNotFound("No element with locator '%s' found."
                                  % locator)
        for element in elements:
            self._style[element]=element.get_attribute('style')
            script = "arguments[0].setAttribute('style', arguments[1]);"
            self.driver.execute_script(script, element, "border: 2px solid red;")

    def apply_original_style(self, locator):
        elements = self.find_elements(locator)
        for element in elements:
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, self._style[element])

    @property
    def log_dir(self):
        try:
            logfile = BuiltIn().get_variable_value('${LOG FILE}')
            if logfile == 'NONE':
                return BuiltIn().get_variable_value('${OUTPUTDIR}')
            return os.path.dirname(logfile)
        except RobotNotRunningError:
            return os.getcwdu() if PY2 else os.getcwd()
