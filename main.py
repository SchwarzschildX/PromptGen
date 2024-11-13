import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QSplitter
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
        self.dir_watcher = QFileSystemWatcher()  # Add this line
        self.dir_watcher.directoryChanged.connect(self.onDirectoryChanged)  # Connect signal
        self.initUI()
        self.loadSettings()

    def initUI(self):
        # Create the main splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Create the tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("File System")

        # Create the text field for the prompt
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your prompt here...")
        self.prompt_edit.textChanged.connect(self.updatePreview)

        # Create the preview text field
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)

        # Create the button
        self.button = QPushButton("Generate Prompt")
        self.button.clicked.connect(self.generatePrompt)

        # Splitter for the right side
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.prompt_edit)
        right_splitter.addWidget(self.preview_edit)

        # Layout for the right side
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_splitter)
        right_layout.addWidget(self.button)

        # Create a QWidget to hold the right layout
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Add widgets to the main splitter
        main_splitter.addWidget(self.tree)
        main_splitter.addWidget(right_widget)

        # Set the main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # Now connect signals and populate the tree
        self.tree.itemExpanded.connect(self.onItemExpanded)
        self.tree.itemChanged.connect(self.updatePreview)
        self.populateTree()

        self.setWindowTitle("Prompt Generator")
        self.show()

        # Store references to splitters for saving/restoring sizes
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
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)  # Add this line

    def onItemExpanded(self, item):
        if not item.data(0, self.RoleIsLoaded):
            item_path = item.data(0, self.RolePath)
            self.addItems(item, item_path)
            item.setData(0, self.RoleIsLoaded, True)
        # Add the directory to the watcher
        dir_path = item.data(0, self.RolePath)
        if os.path.isdir(dir_path):
            if dir_path not in self.dir_watcher.directories():
                self.dir_watcher.addPath(dir_path)
    
    def onItemCollapsed(self, item):
        dir_path = item.data(0, self.RolePath)
        if dir_path in self.dir_watcher.directories():
            self.dir_watcher.removePath(dir_path)

    def onDirectoryChanged(self, path):
        print(f"Directory changed: {path}")
        # Find the item corresponding to this path
        item = self.findItemByPath(path)
        if item:
            # Remove all child items
            item.takeChildren()
            item.setData(0, self.RoleIsLoaded, False)
            # Re-expand the item to reload its contents if it's expanded
            if item.isExpanded():
                self.addItems(item, path)
                item.setData(0, self.RoleIsLoaded, True)

    def findItemByPath(self, path, parent_item=None):
        if parent_item is None:
            parent_item = self.tree.invisibleRootItem()
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child_path = child.data(0, self.RolePath)
            if child_path == path:
                return child
            result = self.findItemByPath(path, child)
            if result:
                return result
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
                item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)  # Add this line
                # Children will be loaded when item is expanded

    def generatePrompt(self):
        full_prompt = self.preview_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(full_prompt)
        print("Prompt copied to clipboard.")

    def getCheckedItems(self, item):
        selected_files = []
        for i in range(item.childCount()):
            child = item.child(i)
            child_path = child.data(0, self.RolePath)
            if child.checkState(0) == Qt.Checked and not os.path.isdir(child_path):
                selected_files.append(child_path)
            elif child.checkState(0) != Qt.Unchecked:
                selected_files.extend(self.getCheckedItems(child))
        return selected_files


    def updatePreview(self):
        prompt_text = self.prompt_edit.toPlainText()
        root_item = self.tree.topLevelItem(0)
        selected_files = self.getCheckedItems(root_item)

        # Update the file watcher
        self.file_watcher.removePaths(self.file_watcher.files())
        if selected_files:
            self.file_watcher.addPaths(selected_files)

        full_prompt = prompt_text
        for file_path in selected_files:
            try:
                # Get the file extension
                _, file_extension = os.path.splitext(file_path)
                normalized_path = os.path.abspath(file_path).replace("\\", "/")

                if file_extension.lower() == '.pdf':
                    # Extract text from PDF
                    content = self.extract_text_from_pdf(file_path)
                else:
                    # Read text from other files
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                full_prompt += f"\n\nFile: {normalized_path}\n\n{content}"
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

        self.preview_edit.setPlainText(full_prompt)


    def onFileChanged(self, path):
        print(f"File changed: {path}")
        self.updatePreview()

    def loadSettings(self):
        # Load the prompt text
        prompt_text = self.settings.value("prompt_text", "")
        self.prompt_edit.setPlainText(prompt_text)
        # Load the checked files
        checked_files = self.settings.value("checked_files", [])
        if checked_files:
            self.checked_files = checked_files  # We'll use this later
            self.restoreCheckedItems()
        # Load the window size
        window_size = self.settings.value("window_size")
        if window_size:
            self.resize(window_size)
        # Load the splitter sizes
        main_splitter_sizes = self.settings.value("main_splitter_sizes")
        if main_splitter_sizes:
            sizes = [int(size) for size in main_splitter_sizes]
            self.main_splitter.setSizes(sizes)
        right_splitter_sizes = self.settings.value("right_splitter_sizes")
        if right_splitter_sizes:
            sizes = [int(size) for size in right_splitter_sizes]
            self.right_splitter.setSizes(sizes)

    def saveSettings(self):
        # Save the prompt text
        self.settings.setValue("prompt_text", self.prompt_edit.toPlainText())
        # Save the checked files
        root_item = self.tree.topLevelItem(0)
        selected_files = self.getCheckedItems(root_item)
        self.settings.setValue("checked_files", selected_files)
        # Save the window size
        self.settings.setValue("window_size", self.size())
        # Save the splitter sizes
        self.settings.setValue("main_splitter_sizes", self.main_splitter.sizes())
        self.settings.setValue("right_splitter_sizes", self.right_splitter.sizes())

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def restoreCheckedItems(self):
        for file_path in self.checked_files:
            self.checkItemByPath(file_path)

    def checkItemByPath(self, file_path):
        root_item = self.tree.topLevelItem(0)
        root_path = root_item.data(0, self.RolePath)
        if not file_path.startswith(root_path):
            return  # The file is not under the root
        relative_path = os.path.relpath(file_path, root_path)
        path_parts = relative_path.split(os.sep)
        current_item = root_item
        for part in path_parts:
            found = False
            # Expand the current item to load its children
            self.tree.expandItem(current_item)  # Added this line
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                if child.text(0) == part:
                    current_item = child
                    found = True
                    break
            if not found:
                return  # Item not found
        # Now, current_item corresponds to the item to check
        current_item.setCheckState(0, Qt.Checked)

    def extract_text_from_pdf(self, file_path):
        content = ''
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {e}")
        return content


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilePromptApp()
    sys.exit(app.exec_())
