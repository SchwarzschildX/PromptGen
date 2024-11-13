# PromptGen

A Python application with a graphical user interface (GUI) that allows users to select files from multiple folders, enter a custom prompt, and generate a combined prompt that includes the contents of the selected files. The combined prompt is displayed in a preview pane and can be copied to the clipboard with a single click.

## Features

- **File Tree with Checkboxes**: Navigate your file system using a tree view. Select or deselect files and folders using checkboxes.
- **Lazy Loading**: The file tree loads directories and files on-demand when expanded, improving performance.
- **Persistent State**: The application remembers your selected files, prompt text, window size, and splitter positions between sessions.
- **Resizable Interface**: Adjust the size of the tree view and text panes using splitters.
- **Live Preview**: See a real-time preview of the combined prompt, including the contents of the selected files.
- **Clipboard Integration**: Copy the combined prompt to your clipboard with a single click.

## Prerequisites

- **Python 3.x**
- **PyQt5**: Install via pip if not already installed.

  ```bash
  pip install PyQt5
  ```
- **PyPDF2**: Install via pip if not already installed.

  ```bash
  pip install PyPDF2
  ```
## Installation

1. **Clone or Download the Repository**

   ```bash
   git clone https://github.com/SchwarzschildX/PromptGen.git
   cd PromptGen
   ```

2. **Install Dependencies**

   Ensure that PyQt5 and PyPDF2 are installed:

   ```bash
   pip install PyQt5 PyPDF2
   ```

## Usage

1. **Run the Application**

   ```bash
   python main.py
   ```

2. **Using the Interface**

   - **File Tree Navigation**

     - The left pane displays your file system starting from your home directory.
     - Expand directories by clicking on the arrow next to a folder.
     - Select files or entire directories by checking the boxes next to them.
     - The application uses lazy loading, so directories load their contents when expanded.

   - **Entering a Prompt**

     - In the top-right text area, enter your custom prompt.
     - This text will precede the contents of the selected files in the combined prompt.

   - **Previewing the Prompt**

     - The bottom-right text area displays a live preview of the combined prompt.
     - It includes your custom prompt and the contents of the selected files.
     - File paths in the prompt are normalized for consistency.

   - **Generating the Prompt**

     - Click the **"Generate Prompt"** button to copy the combined prompt to your clipboard.
     - A message will be printed in the console confirming the action.

3. **Persistent Settings**

   - Your selected files, custom prompt, window size, and splitter positions are saved automatically when you close the application.
   - When you reopen the application, your previous state is restored.

## Configuration

- **Starting Directory**

  - By default, the application starts from your home directory.
  - To change the starting directory, modify the `home_dir` variable in the `populateTree` method of `main.py`:

    ```python
    def populateTree(self):
        home_dir = "path_to_your_directory"  # Replace with your desired path
        # Rest of the method...
    ```

- **File Type Filtering**

  - To display only specific file types (e.g., `.py` files), you can modify the `addItems` method:

    ```python
    def addItems(self, parent, path):
        try:
            items = os.listdir(path)
        except PermissionError:
            return
        for item_name in items:
            item_path = os.path.join(path, item_name)
            if os.path.isdir(item_path):
                # Directory handling...
                pass
            elif item_name.endswith('.py'):
                # Only include .py files
                item = QTreeWidgetItem(parent)
                item.setText(0, item_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
                item.setData(0, self.RolePath, item_path)
                item.setData(0, self.RoleIsLoaded, False)
    ```

## Troubleshooting

- **No GUI Appears**

  - Ensure that PyQt5 is installed and that you're using the correct version of Python.
  - Run `python --version` and `pip show PyQt5` to verify.

- **Permission Issues**

  - The application may not be able to access certain directories or files due to permissions.
  - These directories will not expand, and files will be skipped with a message printed to the console.

- **File Path Issues**

  - On Windows systems, file paths are normalized to use forward slashes for consistency.
  - If you encounter mixed slashes in file paths, ensure you're using the latest version of the code.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue if you find a bug or have a feature request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **PyQt5 Documentation**: [https://www.riverbankcomputing.com/static/Docs/PyQt5/](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- **Python Documentation**: [https://docs.python.org/3/](https://docs.python.org/3/)

---

### LICENSE

```markdown
MIT License

Copyright (c) 2024 SchwarzschildX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

**The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.**

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
**AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY**, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
```