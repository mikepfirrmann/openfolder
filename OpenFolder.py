import sublime, sublime_plugin
from subprocess import call

class OpenFolder(sublime_plugin.WindowCommand):
	def run(self, paths):
		settings = sublime.load_settings("OpenFolder.sublime-settings")
		file_manager = settings.get("file_manager", "xdg-open")
		arg_format = settings.get("arg_format", "{0} '{1}'")

		for path in paths:
			print "Opening {0}".format(path)
			call(arg_format.format(file_manager, path), shell=True)
