import sublime, sublime_plugin
from subprocess import call

class OpenFolder(sublime_plugin.WindowCommand):
	def run(self, paths):
		settings = sublime.load_settings("OpenFolder.sublime-settings")
		file_manager = settings.get("file_manager", "xdg-open")

		for path in paths:
			print "Opening {0}".format(path)
			call("{0} '{1}'".format(file_manager, path), shell=True)
