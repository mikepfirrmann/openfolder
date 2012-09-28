import sublime, sublime_plugin
from subprocess import call

class OpenFolder(sublime_plugin.WindowCommand):
	def run(self, paths):
		settings = sublime.load_settings("OpenFolder.sublime-settings")
		file_manager = settings.get("file_manager", "xdg-open '{0}'")

		for path in paths:
			print "Opening {0}".format(path)
			call(file_manager.format(path), shell=True)
