#!/usr/bin/env python

from main_window import MainWindow
from classifier import Classifier

def main():
    classify = Classifier()
    window = MainWindow(classify)
    window.main()

if __name__ == '__main__':
  main()

# os.path.join(directory, name)

