#!/home/doga/apps/miniconda3/envs/scraping/bin/python

"""
    Call this script with a search keyword to fetch a image from
    wallpaperswide.com and set it as the wallpaper.
"""

import argparse
import subprocess
import logging
from source import WallpapersWide
from source import WallpapersMug


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword', required=False,
                        help='search string')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    wallpaperswide = WallpapersWide()
    wallpapersmug = WallpapersMug()
    #wp_path = wallpaperswide.random_wallpaper(args.keyword)
    wp_path = wallpapersmug.random_wallpaper(args.keyword)
    if wp_path:
        subprocess.run(['feh', '--bg-scale', wp_path])


if __name__ == '__main__':
    main()
