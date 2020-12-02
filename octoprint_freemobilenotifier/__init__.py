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
			login="",
			pass_key="",
			print_events=dict(
					PrintStarted=dict(
							Enabled=False,
							Message="A new print has started! - Filename: {filename}",
							),
					PrintFailed=dict(
							Enabled=False,
							Message="Oh no! The print has failed... - Filename: {filename}",
							),
					PrintCancelled=dict(
							Enabled=False,
							Message="Uh oh... someone cancelled the print! - Filename: {filename}",
							),
					PrintDone=dict(
							Enabled=True,
							Message="Print finished successfully! - Filename: {filename}, Time: {time}",
							),
					PrintPaused=dict(
							Enabled=False,
							Message="Printing has been paused... - Filename: {filename}",
							Color="warning",
							),
					PrintResumed=dict(
							Enabled=False,
							Message="Phew! Printing has been resumed! Back to work... - Filename: {filename}",
							),
					),
			)
	def get_settings_version(self):
		return 1
	
	#~~ TemplatePlugin
	def get_template_configs(self):
		return [dict(type="settings", name="FreeMobile Notifier", custom_bindings=False)]
	
	def on_event(self, event, payload):
		
		events = self._settings.get(['print_events'], merged=True)
		
		if event in events and events[event] and events[event]['Enabled']:
			
				login = self._settings.get(['login'])
				if not login:
						self._logger.exception("Free login is not set!")
						return
				pass_key = self._settings.get(['pass_key'])
				if not pass_key:
						self._logger.exception("Free key is not set!")
						return
					
				filename = payload["name"]
				message = {}
				
				## event settings
				event = self._settings.get(['print_events', event], merged=True)
				
				import datetime
				import octoprint.util
				if "time" in payload and payload["time"]:
						elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=payload["time"]))
				else:
						elapsed_time = ""
						
				message = parse.quote(event['Message'].format(**{'filename': filename, 'time':elapsed_time}))
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
		else:
				self._logger.debug("SMS not configured for event.")
				return
			
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
