#!/usr/bin/env python3

import sys
import os
from PyQt5.QtWidgets import QApplication

# Import the main script
import screenshot

def main():
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Call the main function from the screenshot module
    screenshot.main()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
