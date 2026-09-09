import sys
from config import Config
from plotconfig import PlotConfig
from ui_main import Ui_MainWindow
from PyQt5 import QtWidgets
import head  # Ensure PyInstaller includes head and its dependencies.
app = QtWidgets.QApplication(sys.argv)      # Create the single QApplication instance.

def main():
    cfg = Config()                  # Load the configuration.
    PlotConfig.apply()              # Apply the global font-size configuration.
    window = Ui_MainWindow(cfg)     # Instantiate the main window.
    window.show()                   # Show the window.
    sys.exit(app.exec_())           # Start the Qt event loop and block until the window closes.

if __name__ == "__main__":
    main()
