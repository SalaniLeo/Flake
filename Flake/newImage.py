import sys
from .imageCreator import start
import shutil
from .creator.error import *
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

mainBox = Adw.PreferencesPage.new()
AdvancedInfo = Adw.PreferencesGroup.new()
outputRow = Adw.PreferencesGroup.new()
isOutputActive = False

class newImageBox(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global mainBox
        global AdvancedInfo
        global outputRow

        self.entryNum = 0

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.bottomBox = Gtk.Box()
        self.bottomBox.set_vexpand(True)

        mainBox.set_vexpand(True)
        self.container.append(mainBox)
        self.append(self.container)

        AdvancedInfo = Adw.PreferencesGroup.new()
        AdvancedInfo.set_title("Advanced")

        self.addInfo = Adw.PreferencesGroup.new()
        self.addInfo.set_title("New")

        self.nameEntry = self.newEntryRow("Name", False, "Name",False)
        self.exeEntry = self.newEntryRow("Executable",True,"Executable",False)
        self.iconEntry = self.newEntryRow("Icon", True,"Icon",False)
        self.categoriesEntry = self.newEntryRow("Category",False,"Category",False)
        self.typeEntry = self.newEntryRow("Type",False,"Type",False)

        self.parentFolder = self.newAdvancedRow("Enable folder mode",True, True)
        self.customARLoc = self.newAdvancedRow("Enable custom apprun",True, False)
        AdvancedInfo.add(self.parentFolder)
        AdvancedInfo.add(self.customARLoc)

        self.settings = Gio.Settings.new("io.github.salanileo.flake")
        self.libraryPath = self.settings.get_string("librarypath")
        uselibraryPath = self.settings.get_boolean("uselibrarypath")

        self.addInfo.add(self.nameEntry)
        self.addInfo.add(self.exeEntry)
        self.addInfo.add(self.iconEntry)
        self.addInfo.add(self.categoriesEntry)
        self.addInfo.add(self.typeEntry)
        self.addInfo.set_hexpand(True)

        self.okButton = Gtk.Button(label="confirm")
        self.okButton.set_size_request(80, -1)
        self.okButton.set_halign(Gtk.Align.CENTER)
        self.okButton.set_valign(Gtk.Align.CENTER)
        # self.okButton.connect("clicked", self.confirm)
        self.okButton.set_margin_bottom(6)
        self.okButton.set_margin_top(6)
        self.okButton.connect('clicked', self.createImage)

        mainBox.add(group=self.addInfo)

        self.settings = Gio.Settings.new("io.github.salanileo.flake")
        self.uselibraryPath = self.settings.get_boolean("uselibrarypath")


        self.outputEntry = self.newEntryRow("Location",True,"App location",True)
        outputRow.add(self.outputEntry)
        # mainBox.add(outputRow)

        # print(self.uselibraryPath)
        global isOutputActive

        if self.uselibraryPath:
            isOutputActive = True
            mainBox.add(outputRow)

    def showAdvanced(widget, active):
        global mainBox
        if active is True:
            mainBox.add(AdvancedInfo)
        else:
            mainBox.remove(AdvancedInfo)

    def sameOutput(active, path):
        global mainBox
        global outputRow
        global isOutputActive

        if active:
            if not isOutputActive:
                mainBox.add(outputRow)
        else:
            isOutputActive = False
            mainBox.remove(outputRow)

    def newEntryRow(self, name, buttonNeeded ,placeholder, folderMode):

        label = Gtk.Label(label=name)
        label.set_hexpand(False)
        label.set_halign(Gtk.Align.START)
        entry = Gtk.Entry()
        entry.set_valign(Gtk.Align.CENTER)
        entry.set_halign(Gtk.Align.FILL)
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)

        if name == "Enable folder mode":
            entry.set_placeholder_text("Parent folder location")
        elif name == "Enable custom apprun":
            entry.set_placeholder_text("Custom AppRun location")
        
        global normalRow
        normalRow.append(entry)

        row = Adw.ActionRow.new()
        row.add_suffix(entry)
        row.add_prefix(label)
        if buttonNeeded:
            button = Gtk.Button.new_from_icon_name("document-open-symbolic") 
            button.connect('clicked', self.fileChooser, name, folderMode, entry)
            button.set_valign(Gtk.Align.CENTER)
            row.add_suffix(button)

        return row

    def newAdvancedRow(self, name, buttonNeeded, folderMode):

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)

        label = Gtk.Label(label=name)
        entry = Gtk.Entry()
        entry.set_valign(Gtk.Align.CENTER)
        entry.get_style_context().add_class(class_name='error')
        entry.set_editable(False)
        entry.set_size_request(180,-1)
        if name == "Enable folder mode":
            entry.set_placeholder_text("Parent folder location")
        elif name == "Enable custom apprun":
            entry.set_placeholder_text("Custom AppRun location")
        
        switch.connect('state-set', self.enableOption, entry)

        row = Adw.ActionRow.new()
        row.add_suffix(switch)
        row.add_suffix(entry)
        row.add_prefix(label)

        global advancedRow
        advancedRow.append(entry)

        global advancedSwitch
        advancedSwitch.append(switch)

        if buttonNeeded:
            button = Gtk.Button.new_from_icon_name("document-open-symbolic") 
            button.set_valign(Gtk.Align.CENTER)
            button.connect('clicked', self.fileChooser, name, folderMode, entry)
            row.add_suffix(button)

        return row

    def enableOption(self, switch, state, opt):
        if state == True:
            opt.get_style_context().remove_class(class_name='error')
            opt.set_editable(True)
        elif state == False:
            opt.get_style_context().add_class(class_name='error')
            opt.set_editable(False)


    
    def fileCResponse(self, dialog, window, entry):

            self.dialog.destroy()
            entry.set_text(dialog.get_file().get_path())


    def fileChooser(self, button , title, folderMode, entry):
        
            self.dialog = Gtk.FileChooserNative.new(title=title,
                                                    parent=None, 
                                                    action=Gtk.FileChooserAction.OPEN)

            if folderMode:
                self.dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
            
            self.dialog.show()
            self.dialog.set_title(title)
            self.dialog.connect("response", self.fileCResponse, entry)


    def createImage(self, button):

        nameText = normalRow[0].get_text()
        exeText = normalRow[1].get_text()
        iconText = normalRow[2].get_text()
        typeText = normalRow[3].get_text()
        categoryText = normalRow[4].get_text()

        # self.libraryPath

        outputText = normalRow[5].get_text()

        parentFolderText = advancedRow[0].get_text()
        appRunText = advancedRow[1].get_text()

        parentFolderSwitch = advancedSwitch[0]
        appRunSwitch = advancedSwitch[1]

        if None or "" in (nameText,exeText,iconText,typeText,categoryText,outputText):
            
            throwError(self, "Please fill in all the informations", "All the info are required")

        else:
            
            if(parentFolderSwitch.get_active()):
                folderMode = True
            else:
                folderMode = False

            if(appRunSwitch.get_active()):
                customAppRun = True
            else:
                customAppRun = False

            start(nameText,exeText,iconText,typeText,categoryText,outputText,customAppRun,appRunText,folderMode,parentFolderText,flatpak,self)


    def getFlatpak(isFlatpak):
        global flatpak
        flatpak = isFlatpak


flatpak = None
normalRow = []
advancedRow = []
advancedSwitch = []