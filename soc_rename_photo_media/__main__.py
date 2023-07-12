# -*- coding: UTF-8 -*-


import sys
import logging
import argparse
import shutil

from typing import Dict, List
from soc_rename_photo_media import rename_photo_media

def main():
  rename_photo_media.start()


if __name__ == '__main__':
  main()