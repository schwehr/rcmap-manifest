#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Google Inc. All Rights Reserved.
"""
USGS RCMAP Manifest generation.

gs://ee-nlcd-upload

var dataset = ee.ImageCollection('projects/ee-rcmap/assets/RCMAP_V5_TRENDS/RCMAP_V5_TRENDS');

print(dataset);

What needs MODE?
break_point

Name - Trends (8 areas)      | nodata value
bp_count                     | 101 and 4
pvalue_linear                | 102
slope_linear                 | -32768
total_change_intensity_index | 101
year_recent_break            | 0
bp_year  (yearly)            | None (leave blank)
pvalue_seg  (yearly)         | 102
slope_seg  (yearly)          | -32768

Name - Components (9) | 101
"""
import json

BASE_ID = 'projects/ee-rcmap/assets/RCMAP_V5_TRENDS/'
BUCKET = 'gs://ee-nlcd-upload/rcmap_'

MODE = 'mode'
MEAN = 'mean'

# grep -v '_[0-9]' files.txt  | cut -d\  -f4-
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_break_point.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_bare_ground_break_point.tif
# gs://ee-nlcd-upload/rcmap_bare_ground_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_bare_ground_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_bare_ground_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_herbaceous_break_point.tif
# gs://ee-nlcd-upload/rcmap_herbaceous_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_herbaceous_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_herbaceous_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_litter_break_point.tif
# gs://ee-nlcd-upload/rcmap_litter_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_litter_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_litter_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_non_sagebrush_shrub_break_point.tif
# gs://ee-nlcd-upload/rcmap_non_sagebrush_shrub_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_non_sagebrush_shrub_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_non_sagebrush_shrub_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_perennial_herbaceous_break_point.tif
# gs://ee-nlcd-upload/rcmap_perennial_herbaceous_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_perennial_herbaceous_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_perennial_herbaceous_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_sagebrush_break_point.tif
# gs://ee-nlcd-upload/rcmap_sagebrush_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_sagebrush_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_sagebrush_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_shrub_break_point.tif
# gs://ee-nlcd-upload/rcmap_shrub_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_shrub_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_shrub_most_recent_break_point.tif
# gs://ee-nlcd-upload/rcmap_total_change_intensity_index.tif
# gs://ee-nlcd-upload/rcmap_tree_break_point.tif
# gs://ee-nlcd-upload/rcmap_tree_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_tree_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_tree_most_recent_break_point.tif


# bp_count 101 and 4 - 8bit unsigned - MODE
# bp_year none - 1bit unsigned - MODE
# pvalue_linear 102 - 8bit unsigned - mean
# pvalue_seg 102 - 8bit unsigned - mean
# slope_linear -32768 - 16bit signed - mean
# slope_seg -32768 - 16bit signed -
# total_change_intensity_index 101 - 8bit unsigned - mean
# year_recent_break 0 16bit unsigned MODE

# gs://ee-nlcd-upload/rcmap_annual_herbaceous_break_point.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_linear_model_pvalue.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_linear_model_slope.tif
# gs://ee-nlcd-upload/rcmap_annual_herbaceous_most_recent_break_point.tif

# gs://ee-nlcd-upload/rcmap_total_change_intensity_index.tif

STATS_NON_YEAR = [
    ['break_point', MODE],
    ['linear_model_slope', MEAN],
    ['linear_model_pvalue', MEAN],
    ['most_recent_break_point', MODE]]
# total_change_intensity_index is the band name too.
# MEAN
TOTAL_CHANGE_INTENSITY_INDEX = 'total_change_intensity_index'

# gs://ee-nlcd-upload/rcmap_tree_break_point.tif
# gs://ee-nlcd-upload/rcmap_tree_linear_model_pvalue.tif

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
      entry = {
          'id': name,
          'tilesetId': name,
          # TODO(schwehr): Needed? 'missingData': {'values': [] }
          }
      if averaging == MODE:
        entry['pyramidingPolicy'] = MODE
      bands.append(entry)

  bands.append({
      'id': TOTAL_CHANGE_INTENSITY_INDEX,
      'tilesetId': TOTAL_CHANGE_INTENSITY_INDEX,
  })

  result = {
      'name': BASE_ID + 'RCMAP_V5_TRENDS',
      'tilesets': tilesets,
      # 'bands': bands,
      'startTime': '1985-01-01T00:00:00Z',
      'endTime': '2022-01-01T00:00:00Z',
  }

  return result

# gs://ee-nlcd-upload/rcmap_annual_herbaceous_segment_slope_2021.tif"

LAND_TYPES = [
    'annual_herbaceous', 'bare_ground', 'herbaceous', 'litter', 'sagebrush',
    'shrub', 'non_sagebrush_shrub', 'perennial_herbaceous', 'tree',
]

#  40M 2023/01/03 11:51:46 gs://ee-nlcd-upload/rcmap_shrub_break_point_2021.tif

STAT_TYPES = ['break_point', 'segment_pvalue', 'segment_slope']



def yearly(year: int) -> dict[str, object]:
  """Returns a manifest structure."""
  BUCKET = 'gs://ee-nlcd-upload/rcmap_'

  tilesets = []
  for stat_type in STAT_TYPES:
    for land_type in LAND_TYPES:
      name = f'{land_type}_{stat_type}'
      # gs://ee-nlcd-upload/rcmap_annual_herbaceous_break_point_2021.tif
      # gs://ee-nlcd-upload/rcmap_tree_segment_slope_2004.tif
      path = f'{BUCKET}{land_type}_{stat_type}_{year}.tif'

      # TODO is uris an array or single string
      tilesets.append({'id': name, 'sources': [{'uris': path}]})

  bands = []
  for stat in STAT_TYPES:
    for land in LAND_TYPES:
      name = f'{land}_{stat}'
      entry = {
          'id': name,
          'tilesetId': name,
          # TODO(schwehr): Needed? 'missingData': {'values': [] }
      }
      bands.append(entry)

  result = {
      'name': f'{BASE_ID}RCMAP_V5_TRENDS_year/{year}',
      'tilesets': tilesets,
      'bands': bands,
      'startTime': f'{year}-01-01T00:00:00Z',
      'endTime': f'{year+1}-01-01T00:00:00Z',
  }

  return result


def main():
  print(json.dumps(trends(), indent=2))
  print('\n\n========================\n\n')

  # print(json.dumps(yearly(2021), indent=2))
  # for year in range(1985, 2022):
  #   print(f'\n\n==================== {year} ====================\n\n')
  #   print(json.dumps(yearly(year), indent=2))

if __name__ == '__main__':
  main()
