# coding=utf-8
#
# This file is part of SickGear.
#
# Thanks to: mallen86
#
# SickGear is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickGear is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickGear.  If not, see <http://www.gnu.org/licenses/>.

import json
import sickbeard

from sickbeard import logger, common

class SlackNotifier:

    def _send_to_slack(self, message, accessToken, channel, as_user, bot_name, icon_url):
        SLACK_ENDPOINT = "https://slack.com/api/chat.postMessage"

        data = {}
        data["token"] = accessToken
        data["channel"] = channel
        data["username"] = bot_name
        data["text"] = message
        data["icon_url"] = icon_url
        data["as_user"] = as_user

        urlResp = sickbeard.helpers.getURL(url=SLACK_ENDPOINT, post_data=data)
        if urlResp:
            resp = json.loads(urlResp)
        else:
            return False

        # if ("error" in resp):
        #     raise Exception(resp["error"])

        if (resp["ok"] == True):
            logger.log(u"Slack: Succeeded sending message.", logger.MESSAGE)
            return True

        logger.log(u"Slack: Failed sending message: " + resp["error"], logger.ERROR)
        return False

    def _notify(self, message, accessToken='', channel='', as_user='', bot_name='', icon_url='', force=False):
        # suppress notifications if the notifier is disabled but the notify options are checked
        if not sickbeard.USE_SLACK and not force:
            return False

        if not accessToken:
            accessToken = sickbeard.SLACK_ACCESS_TOKEN
        if not channel:
            channel = sickbeard.SLACK_CHANNEL
        if not as_user:
            as_user = sickbeard.SLACK_AS_USER
        if not bot_name:
            bot_name = sickbeard.SLACK_BOT_NAME
        if not icon_url:
            icon_url = sickbeard.SLACK_ICON_URL

        return self._send_to_slack(message, accessToken, channel, as_user, bot_name, icon_url)

##############################################################################
# Public functions
##############################################################################

    def notify_snatch(self, ep_name):
        if sickbeard.SLACK_NOTIFY_ONSNATCH:
            self._notify(common.notifyStrings[common.NOTIFY_SNATCH] + ': ' + ep_name)

    def notify_download(self, ep_name):
        if sickbeard.SLACK_NOTIFY_ONDOWNLOAD:
            self._notify(common.notifyStrings[common.NOTIFY_DOWNLOAD] + ': ' + ep_name)

    def test_notify(self, accessToken, channel, as_user, bot_name, icon_url):
        return self._notify("This is a test notification from SickGear", accessToken, channel, as_user, bot_name, icon_url, force=True)

    def update_library(self, ep_obj):
        pass

notifier = SlackNotifier
