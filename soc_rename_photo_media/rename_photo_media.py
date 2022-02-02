# -*- encoding: utf-8 -*-

import os
import sys
import re

import time
from datetime import date, datetime, timedelta
import multiprocessing
import traceback

import config

import exifread
from pymediainfo import MediaInfo

from utils import log_utils, file_utils


def get_photo_create_time(file_path):
  global _logger
  f = open(file_path, 'rb')

  try:
    tags = exifread.process_file(f)

    dt = tags.get('EXIF DateTimeOriginal', None) if tags.get('EXIF DateTimeOriginal', None) != None else tags.get(
        'Image DateTime', '')
    if None is dt or '' == dt:
      dt = os.stat(file_path).st_mtime
      if None is not dt:
        dt = datetime.fromtimestamp(dt).strftime('%Y%m%d_%H%M%S')

    dt = str(dt).replace(' ', '_').replace(':', '')
    return dt
  except Exception as e:
    _logger.info(traceback.format_exc())
    return None
  finally:
    f.close()


def utc_time_to_local(strtime):
  return (datetime.strptime(strtime, 'UTC %Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%Y%m%d_%H%M%S')


def duration_to_time(duration):
  if None is duration:
    return '0'
  d = duration / 1000
  if d <= 60:
    return '%d秒' % d
  if d <= 3600:
    return '%d分%d秒' % (d / 60, d % 60)
  d1 = d % 3600
  return '%d时%d分%d秒' % (d / 3600, d1 / 60, d1 % 60)


def get_media_info(file_path):
  media_info = MediaInfo.parse(file_path)

  m = {
      'date': '',
      'duration': 0,
  }
  # print(media_info.to_json())
  for track in media_info.tracks:
    if track.track_type == 'General':
      d = track.encoded_date
      if d is None:
        d = track.tagged_date
      if d is None:
        d = str(track.file_last_modification_date)[:23]

      if d is not None:
        m['date'] = utc_time_to_local(d)
      else:
        m['date'] = ''

      duration = track.duration
      if isinstance(duration, str):
        duration = int(float(duration))
      m['duration'] = duration_to_time(duration)

  return m


def rename(oldPath, newPath, oldNefPath=None, newNefPath=None):
  file_utils.move(oldPath, newPath)
  if None is not oldNefPath and file_utils.is_file(oldNefPath):
    file_utils.move(oldNefPath, newNefPath)


def rename_photo(file_path, file_path_info, suffix):
  global _pre_name
  nef = '.NEF'

  dt = get_photo_create_time(file_path)

  new_photo_path = '%s\\%s_%s%s' % (file_path_info[0], _pre_name, dt, suffix)

  old_nef_path = os.path.join(file_path_info[0], file_path_info[1].replace(suffix, nef))
  new_nef_path = '%s\\%s_%s%s' % (file_path_info[0], _pre_name, dt, nef)

  if file_path == new_photo_path:
    return new_photo_path

  if not file_utils.is_file(new_photo_path):
    rename(file_path, new_photo_path, old_nef_path, new_nef_path)
    return new_photo_path

  for i in range(1, 100):

    new_photo_path = '%s\\%s_%s_%d%s' % (file_path_info[0], _pre_name, dt, i, suffix)
    new_nef_path = '%s\\%s_%s_%d%s' % (file_path_info[0], _pre_name, dt, i, nef)

    if not file_utils.is_file(new_photo_path):
      rename(file_path, new_photo_path, old_nef_path, new_nef_path)
      return new_photo_path
  return None


def rename_media(file_path, file_path_info, suffix):
  global _pre_name

  info = get_media_info(file_path)

  new_media_path = '%s\\%s_%s_%s%s' % (
      file_path_info[0], _pre_name, info['date'], info['duration'], suffix)

  if not file_utils.is_file(new_media_path):
    rename(file_path, new_media_path)
    return new_media_path

  for i in range(1, 100):
    new_media_path = '%s\\%s_%s_%s_%d%s' % (
        file_path_info[0], _pre_name, info['date'], info['duration'], i, suffix)
    if not file_utils.is_file(new_media_path):
      rename(file_path, new_media_path)
      return new_media_path
  return None


def rename_file(file_path_info):
  global _pre_name

  file_path = os.path.join(file_path_info[0], file_path_info[1])
  suffix = os.path.splitext(file_path)[-1].lower()

  if '.nef' in suffix:
    return None
  if suffix in config.IMG_SUFFIX:
    rename_photo(file_path, file_path_info, suffix)
  if suffix in config.MEDIA_SUFFIX:
    rename_media(file_path, file_path_info, suffix)


def rename_files():
  global _cpu_count, _logger, _file_folder
  files = file_utils.walk2(_file_folder)

  for file in files:
    rename_file(file)

  # print(files)
  # pool = multiprocessing.Pool(processes=_cpu_count)
  # print(pool)
  # print(pool.map(rename_file, files))


def init():
  global _logger, _cpu_count
  _cpu_count = multiprocessing.cpu_count()
  _logger = log_utils.get_logger('./log.log')
  rename_files()


def start():
  init()


_file_folder = 'F:\\202107贵州'
_pre_name = '202107贵州'
_logger = None
_cpu_count = 1
_date_format = '%Y-%m-%d %H:%M:%S'


def f(x):
  return x*x


def start_map():
  _cpu_count = multiprocessing.cpu_count()
  print(_cpu_count)
  pool = multiprocessing.Pool(processes=_cpu_count)
  r = pool.map(f, [100])
  print(f)
  pool.close()
  pool.join()


if __name__ == '__main__':
  start()
  # start_map()
