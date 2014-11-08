#!/usr/bin/env python

from classifier import Classifier
from main_window import MainWindow

def main():
    classify = Classifier()
    window = MainWindow(classify)
    window.main()

if __name__ == '__main__':
  main()

