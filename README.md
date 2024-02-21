
# Libre-Case

**Libre-Case** is a versatile utility software designed for direct in-place case conversions across a multitude of applications. By seamlessly integrating with numerous programs, it offers an efficient solution for transforming text instantly, enhancing productivity for coding, document composition, and data management.
Specifically developed for and tested only on Windows, it leverages the unique capabilities of the Windows operating system to deliver its functionality.

## Features

**Libre-Case** boasts a comprehensive set of features for comprehensive text manipulation:

- **UPPERCASE**: Converts text to all uppercase letters for emphasis or coding standards.
- **lowercase**: Transforms text to all lowercase letters for a consistent appearance.
- **Title Case**: Capitalizes the first letter of each word, ideal for titles and headings.
- **Sentence case**: Converts text to sentence case, capitalizing the first letter of sentences.
- **Reverse**: Reverses the order of characters in text for encoding or playful purposes.
- **Remove Extra Lines**: Cleans up text by removing unnecessary blank lines.
- **Remove Extra Spaces**: Eliminates extra spaces between words for streamlined text.
- **Count Words**: Provides an instant word count, useful for meeting word limits.
- **Count Characters**: Offers a character count, with or without spaces.
- **Alternating Case**: Converts text to alternating case for a distinctive style.
- **Invert Case**: Inverts the case of each letter, making uppercase letters lowercase and vice versa.

### Quick Conversion: Select Text -> Use Shortcut -> Convert

## Platform Availability

Libre-Case is currently available and has been rigorously tested exclusively on the Windows operating system. Users of other platforms should note that compatibility and functionality cannot be guaranteed outside of a Windows environment.

## Usage

Libre-Case is designed to start automatically upon system startup and runs unobtrusively in the background.

### Keyboard Shortcuts:
To activate, simply select the text, then press `Ctrl + Shift + L` to bring up the conversion menu.

## Installation

**Libre-Case** is conveniently packaged as a portable application, requiring no formal installation.

To use Libre-Case:
1. Download the latest release from the official website.
2. Extract the contents of the ZIP file.
3. Run `libre-case-runner.bat`.

The application will launch minimized in the system tray, ready for use.

## Contributing

We welcome contributions of all kinds! For more information on how to contribute, please consult the `CONTRIBUTING.md` document in our repository.

## License

**Libre-Case** is made available under the MIT License. For more details, see the `LICENSE` file included with the distribution.

## Credits

**Libre-Case** was developed by Mr. Lacarte, with contributions from the open-source community.

## Contact

For support, suggestions, or contributions, please reach out to us through our project repository or contact Mr. Lacarte directly via email dev.lacarte@gmail.com.





  
### To set venv() to the .venv directory 

    python -m venv .venv

  
### To activate venv 

    .venv\Scripts\activate.bat


### To deactivate venv

    .venv\Scripts\deactivate.bat

  
### To backup libraries

#### Only top dependencies 
    pip install pipdeptree
     
    pipdeptree -f --warn silence | findstr  /r  "^[a-zA-Z0-9\-]" > requirements.txt
  
    pipdeptree --warn silence --freeze  --warn silence | grep -v '^\s' > requirements.txt
  
### To install libraries

    pip install -r requirements.txt
