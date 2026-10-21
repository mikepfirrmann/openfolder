import sublime
import sublime_plugin
import subprocess
import os
import os.path
import platform

# Patch for ST2
# Works because ST2 unpacks the plugins before running them
if __package__ is None:
    __package__ = os.path.basename(os.getcwd())


class OpenFolderClassicCommand(object):
    def __init__(self, window, cmdline):
        self.window = window
        self.cmdline = cmdline

    def runForFolder(self, folderPath):
        subprocess.call(self.cmdline.format(folderPath), shell=True)

    def runForFile(self, filePath):
        self.window.run_command(
            "open_dir",
            {
                "dir": os.path.dirname(filePath),
                "file": os.path.basename(filePath)
            }
        )


class OpenFolderCommand(object):
    def __init__(self, window, folder_command, file_command):
        self.window = window
        self.folder_command = folder_command
        self.file_command = file_command

    def runForFolder(self, folderPath):
        pieces = self.parseFolder(folderPath)

        if self.folder_command is None:
            raise RuntimeError('There are not commands configurated')
        else:
            use_shell = False
            if 'use_shell' in self.folder_command:
                use_shell = bool(self.folder_command['use_shell'])

            self.execute(self.folder_command['command'], pieces, use_shell)

    def runForFile(self, filePath):
        pieces = self.parseFile(filePath)

        if self.file_command is None:
            if self.folder_command is not None:
                return self.runForFolder(pieces['dirname'])
            else:
                raise RuntimeError('There are not commands configurated')
        else:
            use_shell = False
            if 'use_shell' in self.file_command:
                use_shell = bool(self.file_command['use_shell'])

            self.execute(self.file_command['command'], pieces, use_shell)

    def parseFolder(self, path):
        return {
            'filepath': path,
            'dirname': path,
            'basename': ''
        }

    def parseFile(self, path):
        return {
            'filepath': path,
            'dirname': os.path.dirname(path),
            'basename': os.path.basename(path)
        }

    def execute(self, cmd, filler, use_shell):
        try:
            cmd_list = [item.format(**filler) for item in cmd]
        except KeyError as err:
            return sublime.status_message(
                "{0} is not a valid replacement".format(err.args[0])
            )
        except Exception as err:
            return sublime.status_message(repr(err))

        cwd = filler['dirname']

        try:
            subprocess.Popen(cmd_list, shell=use_shell, cwd=cwd)
        except Exception as err:
            sublime.status_message(repr(err))


class OpenFolderHelper(object):
    @classmethod
    def getCommand(cls, window):
        helper = cls()
        classic_cmdline = helper.getSetting("file_manager")

        if classic_cmdline is not None:
            return OpenFolderClassicCommand(window, classic_cmdline)

        return OpenFolderCommand(
            window, helper.getSetting('folder'), helper.getSetting('file')
        )

    @classmethod
    def getPlatformSettingsFilePath(cls):
        return cls.getSettingsFilePath(sublime.platform().capitalize())

    @classmethod
    def getHostSettingsFilePath(cls):
        return cls.getSettingsFilePath(platform.uname()[1])

    @classmethod
    def getSettingsFilePath(cls, special=None):
        special = " (" + special + ")" if special else ""
        return "".join(("OpenFolder", special, ".sublime-settings"))

    def __init__(self):
        self.host_settings = sublime.load_settings(
            OpenFolderHelper.getHostSettingsFilePath())

        self.user_settings = sublime.load_settings(
            OpenFolderHelper.getSettingsFilePath())

    def getSetting(self, settingName, default=None):
        return self.host_settings.get(
            settingName, self.user_settings.get(settingName, default))


class OpenFolder(sublime_plugin.WindowCommand):
    def run(self, paths):
        command = OpenFolderHelper.getCommand(self.window)

        for path in paths:
            if os.path.isdir(path):
                command.runForFolder(path)
            else:
                command.runForFile(path)

    def description(self, paths):
        helper = OpenFolderHelper()

        display_for_files = helper.getSetting('display_for_files', True)

        file_count = 0
        dir_count = 0

        for path in paths:
            if os.path.isdir(path):
                dir_count += 1
            else:
                file_count += 1

        if dir_count > 1 or (dir_count > 0 and file_count > 0):
            return "Open Folders"
        elif dir_count == 1:
            return "Open Folder"
        elif file_count > 1 and display_for_files:
            return u"Open Containing Folders\u2026"
        elif file_count > 0 and display_for_files:
            return u"Open Containing Folder\u2026"
        else:
            return None


class OpenFolderOpenSettings(sublime_plugin.WindowCommand):
    # Allows the opening of Default plugin settings files even if running from
    # a packaged plugin. Also, adds support for host-specific settings using a
    # hack on sublime.load_settings().

    def run(self, scope='default'):
        settingsFilePieces = self.getSettingPieces(scope)

        self.window.run_command("open_file", {
            "file": "${packages}/%0s/%1s" % settingsFilePieces
        })

    def getSettingPieces(self, scope):
        if scope == 'host':
            return ('User/', OpenFolderHelper.getHostSettingsFilePath())
        elif scope == 'user':
            return ('User/', OpenFolderHelper.getSettingsFilePath())
        elif scope == 'os':
            return (__package__, OpenFolderHelper.getPlatformSettingsFilePath())
        else:  # default
            return (__package__, OpenFolderHelper.getSettingsFilePath())


class OpenFolderOpenCurrent(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.file_name() is not None:
            self.view.window().run_command('open_folder', {
                'paths': [self.view.file_name()]
            })
