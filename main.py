import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QSplitter, QCheckBox
)
from PyQt5.QtCore import Qt, QSettings, QFileSystemWatcher
import PyPDF2

class FilePromptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "FilePromptApp")
        self.RoleIsLoaded = Qt.UserRole + 1
        self.RolePath = Qt.UserRole + 2
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.onFileChanged)
        self.dir_watcher = QFileSystemWatcher()
        self.dir_watcher.directoryChanged.connect(self.onDirectoryChanged)
        self.initUI()
        self.loadSettings()

    def initUI(self):
        main_splitter = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("File System")

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your prompt here...")
        self.prompt_edit.textChanged.connect(self.updatePreview)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by extensions (e.g: '.txt, .py')")
        self.filter_edit.textChanged.connect(self.filter_tree_items)

        self.ignore_dot_files_checkbox = QCheckBox("Ignore dot files")
        self.ignore_dunder_checkbox = QCheckBox("Ignore __ files")
        self.ignore_dot_files_checkbox.stateChanged.connect(self.filter_tree_items)
        self.ignore_dunder_checkbox.stateChanged.connect(self.filter_tree_items)

        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)

        self.button = QPushButton("Generate Prompt")
        self.button.clicked.connect(self.generatePrompt)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.prompt_edit)
        right_splitter.addWidget(self.preview_edit)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.ignore_dot_files_checkbox)
        checkbox_layout.addWidget(self.ignore_dunder_checkbox)
        checkbox_layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.addLayout(checkbox_layout)
        right_layout.addWidget(self.filter_edit)
        right_layout.addWidget(right_splitter)
        right_layout.addWidget(self.button)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_splitter.addWidget(self.tree)
        main_splitter.addWidget(right_widget)

        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        self.tree.itemExpanded.connect(self.onItemExpanded)
        self.tree.itemCollapsed.connect(self.onItemCollapsed)
        self.tree.itemChanged.connect(self.updatePreview)
        self.populateTree()

        self.setWindowTitle("Prompt Generator")
        self.show()
        self.main_splitter = main_splitter
        self.right_splitter = right_splitter

    def populateTree(self):
        home_dir = os.path.expanduser("C:/")
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, home_dir)
        root_item.setFlags(root_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        root_item.setCheckState(0, Qt.Unchecked)
        root_item.setData(0, self.RolePath, home_dir)
        root_item.setData(0, self.RoleIsLoaded, False)
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

    def onItemExpanded(self, item):
        if not item.data(0, self.RoleIsLoaded):
            item_path = item.data(0, self.RolePath)
            self.addItems(item, item_path)
            item.setData(0, self.RoleIsLoaded, True)
        dir_path = item.data(0, self.RolePath)
        if os.path.isdir(dir_path) and dir_path not in self.dir_watcher.directories():
            self.dir_watcher.addPath(dir_path)
        self.filter_tree_items()

    def onItemCollapsed(self, item):
        dir_path = item.data(0, self.RolePath)
        if dir_path in self.dir_watcher.directories():
            self.dir_watcher.removePath(dir_path)

    def onDirectoryChanged(self, path):
        item = self.findItemByPath(path)
        if item:
            existing_items = {child.text(0): child for i in range(item.childCount()) if (child := item.child(i))}
            try:
                new_names = os.listdir(path)
            except PermissionError:
                new_names = []
            new_names_set = set(new_names)
            for name in list(existing_items.keys()):
                if name not in new_names_set:
                    item.removeChild(existing_items[name])
            for name in new_names:
                if name not in existing_items:
                    child_path = os.path.join(path, name)
                    child_item = QTreeWidgetItem(item)
                    child_item.setText(0, name)
                    child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                    child_item.setCheckState(0, Qt.Unchecked)
                    child_item.setData(0, self.RolePath, child_path)
                    child_item.setData(0, self.RoleIsLoaded, False)
                    if os.path.isdir(child_path):
                        child_item.setFlags(child_item.flags() | Qt.ItemIsTristate)
                        child_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            self.tree.update()
            self.filter_tree_items()

    def findItemByPath(self, path, parent_item=None):
        if parent_item is None:
            parent_item = self.tree.invisibleRootItem()
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.data(0, self.RolePath) == path:
                return child
            if found := self.findItemByPath(path, child):
                return found
        return None

    def addItems(self, parent, path):
        try:
            items = os.listdir(path)
        except PermissionError:
            return
        for item_name in items:
            item_path = os.path.join(path, item_name)
            item = QTreeWidgetItem(parent)
            item.setText(0, item_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setData(0, self.RolePath, item_path)
            item.setData(0, self.RoleIsLoaded, False)
            if os.path.isdir(item_path):
                item.setFlags(item.flags() | Qt.ItemIsTristate)
                item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

    def generatePrompt(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_edit.toPlainText())
        print("Prompt copied to clipboard.")

    def getCheckedItems(self, item):
        selected_files = []
        for i in range(item.childCount()):
            child = item.child(i)
            # Skip items that are hidden (i.e. filtered out).
            if child.isHidden():
                continue
            child_path = child.data(0, self.RolePath)
            # Only add non-directory files that are visible and checked.
            if child.checkState(0) == Qt.Checked and not os.path.isdir(child_path):
                selected_files.append(child_path)
            selected_files.extend(self.getCheckedItems(child))
        return selected_files


    def updatePreview(self):
        current_files = self.file_watcher.files()
        if current_files:
            self.file_watcher.removePaths(current_files)
        selected_files = self.getCheckedItems(self.tree.topLevelItem(0))
        if selected_files:
            self.file_watcher.addPaths(selected_files)
        prompt_text = self.prompt_edit.toPlainText()
        full_prompt = prompt_text
        for file_path in selected_files:
            try:
                _, ext = os.path.splitext(file_path)
                normalized_path = os.path.abspath(file_path).replace("\\", "/")
                content = self.extract_text_from_pdf(file_path) if ext.lower() == '.pdf' else open(file_path, 'r', encoding='utf-8', errors='ignore').read()
                full_prompt += f"\n\nFile: {normalized_path}\n\n```\n{content}\n```"
            except Exception as e:
                print(f"Could not read {file_path}: {e}")
        self.preview_edit.setPlainText(full_prompt)

    def onFileChanged(self, path):
        self.updatePreview()

    def loadSettings(self):
        self.prompt_edit.setPlainText(self.settings.value("prompt_text", ""))
        self.filter_edit.setText(self.settings.value("filter_text", ""))
        self.ignore_dot_files_checkbox.setChecked(self.settings.value("hide_dot_files", False, type=bool))
        self.ignore_dunder_checkbox.setChecked(self.settings.value("hide_dunder", False, type=bool))
        if window_size := self.settings.value("window_size"):
            self.resize(window_size)
        if main_sizes := self.settings.value("main_splitter_sizes"):
            self.main_splitter.setSizes([int(s) for s in main_sizes])
        if right_sizes := self.settings.value("right_splitter_sizes"):
            self.right_splitter.setSizes([int(s) for s in right_sizes])
        self.checked_files = self.settings.value("checked_files", [])
        self.restoreCheckedItems()

    def saveSettings(self):
        self.settings.setValue("prompt_text", self.prompt_edit.toPlainText())
        self.settings.setValue("checked_files", self.getCheckedItems(self.tree.topLevelItem(0)))
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("main_splitter_sizes", self.main_splitter.sizes())
        self.settings.setValue("right_splitter_sizes", self.right_splitter.sizes())
        self.settings.setValue("filter_text", self.filter_edit.text())
        self.settings.setValue("hide_dot_files", self.ignore_dot_files_checkbox.isChecked())
        self.settings.setValue("hide_dunder", self.ignore_dunder_checkbox.isChecked())

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def restoreCheckedItems(self):
        for path in self.checked_files:
            self.checkItemByPath(path)

    def checkItemByPath(self, file_path):
        root_item = self.tree.topLevelItem(0)
        root_path = root_item.data(0, self.RolePath)
        if not file_path.startswith(root_path):
            return
        parts = os.path.relpath(file_path, root_path).split(os.sep)
        current_item = root_item
        for part in parts:
            self.tree.expandItem(current_item)
            found = False
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                if child.text(0) == part:
                    current_item = child
                    found = True
                    break
            if not found:
                return
        current_item.setCheckState(0, Qt.Checked)

    def extract_text_from_pdf(self, file_path):
        content = ''
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return content

    def filter_tree_items(self):
        filter_ext = [ext.strip().lower() for ext in self.filter_edit.text().split(',')] if self.filter_edit.text() else []
        self.recursive_filter_items(self.tree.invisibleRootItem(), filter_ext)

    def recursive_filter_items(self, item, filter_ext):
        any_child_visible = False
        for i in range(item.childCount()):
            child = item.child(i)
            child_visible = self.recursive_filter_items(child, filter_ext)
            any_child_visible |= child_visible
            child.setHidden(not child_visible)
        if item == self.tree.invisibleRootItem():
            return True  # Always process the invisible root

        item_name = item.text(0)
        _, ext = os.path.splitext(item_name.lower())
        item_path = item.data(0, self.RolePath)
        is_dir = os.path.isdir(item_path)
        
        # Directories always "match" the extension filter.
        matches_filter = True if is_dir else (ext in filter_ext if filter_ext else True)
        
        # Use the new checkbox names.
        ignore_dot = self.ignore_dot_files_checkbox.isChecked() and item_name.startswith('.')
        ignore_dunder = self.ignore_dunder_checkbox.isChecked() and item_name.startswith('__')
        
        # Item is visible if it matches the filter or has visible children and isn't being ignored.
        item_visible = (matches_filter or any_child_visible) and not (ignore_dot or ignore_dunder)
        
        # Always show the top-level item.
        if item is self.tree.topLevelItem(0):
            item_visible = True

        item.setHidden(not item_visible)
        return item_visible


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilePromptApp()
    sys.exit(app.exec_())