# coding=utf-8

from __future__ import absolute_import
import os
import sys
import octoprint.plugin

from future import standard_library
standard_library.install_aliases()
from urllib import request,parse

class FreemobilenotifierPlugin(octoprint.plugin.EventHandlerPlugin,
                               octoprint.plugin.SettingsPlugin,
                               octoprint.plugin.AssetPlugin,
                               octoprint.plugin.TemplatePlugin):

	#~~ SettingsPlugin
	def get_settings_defaults(self):
		return dict(
			enabled=False,
			login="",
			pass_key="",
			message_format=dict(
				body="Job complete: {filename} done printing after {elapsed_time}"
			)
		)

	def get_settings_version(self):
		return 1

	#~~ TemplatePlugin
	def get_template_configs(self):
		return [dict(type="settings", name="FreeMobile Notifier", custom_bindings=False)]

	#~~ EventPlugin
	def on_event(self, event, payload):
		if event != "PrintDone":
			return

		if not self._settings.get(['enabled']):
			return

		filename = payload["name"]

		import datetime
		import octoprint.util
		elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=payload["time"]))

		tags = {'filename': filename, 'elapsed_time': elapsed_time}
		message = parse.quote(self._settings.get(["message_format", "body"]).format(**tags))
		login = self._settings.get(["login"])
		pass_key = self._settings.get(["pass_key"])
		url = 'https://smsapi.free-mobile.fr/sendmsg?&user='+login+'&pass='+pass_key+'&msg='+message

		try:
				request.urlopen(url)
		except Exception as e:
			# report problem sending sms
			self._logger.exception("SMS notification error: %s" % (str(e)))
		else:
			# report notification was sent
			self._logger.info("Print notification sent to %s" % (self._settings.get(['login'])))

	##~~ Softwareupdate hook
	def get_update_information(self):
		return dict(
			freemobilenotifier=dict(
				displayName="FreeMobile Notifier",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Pinaute",
				repo="OctoPrint_FreeMobile-Notifier",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/Pinaute/OctoPrint_FreeMobile-Notifier/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "FreeMobile Notifier"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = FreemobilenotifierPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
