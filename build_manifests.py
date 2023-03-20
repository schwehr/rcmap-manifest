#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Google Inc. All Rights Reserved.
"""
USGS RCMAP Manifest generation.

gs://ee-nlcd-upload

var trends = ee.Image('projects/ee-rcmap/assets/RCMAP_V5_TRENDS/TRENDS');
var dataset = ee.ImageCollection('projects/ee-rcmap/assets/RCMAP_V5_TRENDS/YEAR');

print(dataset);
"""
import json

BASE_ID = 'projects/ee-rcmap/assets/RCMAP_V5_TRENDS/'
BUCKET = 'gs://ee-nlcd-upload/rcmap_'

MODE = 'mode'
MEAN = 'mean'

STATS_NON_YEAR = [
    ['break_point', MODE],
    ['linear_model_slope', MEAN],
    ['linear_model_pvalue', MEAN],
    ['most_recent_break_point', MODE]]
# total_change_intensity_index is the band name too - MEAN
TOTAL_CHANGE_INTENSITY_INDEX = 'total_change_intensity_index'


def trends() -> dict[str, object]:
  """Returns a manifest structure."""
  tilesets = []
  for stat, unused_averaging in STATS_NON_YEAR:
    for land in LAND_TYPES:
      name = f'{land}_{stat}'
      tilesets.append({
          'id': name,
          'sources': [{'uris': BUCKET + name + '.tif'}]})

  tilesets.append({
      'id': TOTAL_CHANGE_INTENSITY_INDEX,
      'sources': [{'uris': BUCKET + TOTAL_CHANGE_INTENSITY_INDEX + '.tif'}]})

  bands = []
  for stat, averaging in STATS_NON_YEAR:
    for land in LAND_TYPES:
      name = f'{land}_{stat}'
      entry = {'id': name, 'tilesetId': name}
      if averaging == MODE:
        entry['pyramidingPolicy'] = MODE
      bands.append(entry)

  bands.append({
      'id': TOTAL_CHANGE_INTENSITY_INDEX,
      'tilesetId': TOTAL_CHANGE_INTENSITY_INDEX,
  })

  result = {
      'name': BASE_ID + 'TRENDS',
      'tilesets': tilesets,
      'bands': bands,
      'startTime': '1985-01-01T00:00:00Z',
      'endTime': '2022-01-01T00:00:00Z',
  }

  return result


LAND_TYPES = [
    'annual_herbaceous', 'bare_ground', 'herbaceous', 'litter', 'sagebrush',
    'shrub', 'non_sagebrush_shrub', 'perennial_herbaceous', 'tree',
]

STAT_TYPES = ['break_point', 'segment_pvalue', 'segment_slope']


def yearly(year: int) -> dict[str, object]:
  """Returns a manifest structure."""
  BUCKET = 'gs://ee-nlcd-upload/rcmap_'

  tilesets = []
  for stat_type in STAT_TYPES:
    for land_type in LAND_TYPES:
      name = f'{land_type}_{stat_type}'
      path = f'{BUCKET}{land_type}_{stat_type}_{year}.tif'

      tilesets.append({'id': name, 'sources': [{'uris': [path]}]})

  bands = []
  for stat in STAT_TYPES:
    for land in LAND_TYPES:
      name = f'{land}_{stat}'
      entry = {'id': name, 'tilesetId': name}
      bands.append(entry)

  result = {
      'name': f'{BASE_ID}YEAR/{year}',
      'tilesets': tilesets,
      'bands': bands,
      'startTime': f'{year}-01-01T00:00:00Z',
      'endTime': f'{year+1}-01-01T00:00:00Z',
  }

  return result


def main():
  trends_json = json.dumps(trends(), indent=2)
  print(trends_json)

  with open('rcmap_trends_manifest.json', 'w') as out:
    out.write(trends_json)

  print('\n\n========================\n\n')

  print(json.dumps(yearly(2021), indent=2))

  for year in range(1985, 2022):
    yearly_json = json.dumps(yearly(year), indent=2)
    with open(f'rcmap_{year}_manifest.json', 'w') as out:
      out.write(yearly_json)


if __name__ == '__main__':
  main()
