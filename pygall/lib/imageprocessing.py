# -*- coding: utf-8 -*-
import os
import datetime
import shutil
import logging
from types import StringType, UnicodeType
from imghdr import what

import Image
import ExifTags

from pygall.lib.helpers import img_md5

log = logging.getLogger(__name__)

# CONSTANTS
ORIG = "orig"
SCALED = "scaled"

class ImageProcessing:
    def __init__(self,
                 dest_dir,
                 crop_dimension=700,
                 crop_quality=80):
        self.dest_dir = dest_dir
        self.abs_orig_dest_dir = os.path.join(self.dest_dir, ORIG)
        self.abs_scaled_dest_dir = os.path.join(self.dest_dir, SCALED)
        self.dimension = crop_dimension
        self.quality = crop_quality

    def copy_orig(self, src, dest_uri):
        """
        Copy the original image to orig dest directory
        """
        dest = os.path.join(self.abs_orig_dest_dir, dest_uri)

        if not self._check_paths(src, dest):
            return

        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)
        if isinstance(src, (StringType, UnicodeType)):
            shutil.copyfile(src, dest)
        else:
            with open(dest, 'wb') as f:
                shutil.copyfileobj(src, f)
        log.info("Copied: %s" % dest)


    def copy_scaled(self, src, dest_uri):
        """
        Rotate and scale image.
        Copy the processed image to scaled dest directory
        """
        dest = os.path.join(self.abs_scaled_dest_dir, dest_uri)

        if not self._check_paths(src, dest):
            return

        try:
            orientation = self._get_exif(src)['Orientation']
        except:
            orientation = 0

        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)

        im = Image.open(src)
        # auto rotate if needed
        if orientation == 6:
            im=im.rotate(270)
        if orientation == 8:
            im=im.rotate(90)

        width_src, height_src = im.size
        if width_src <= self.dimension and height_src <= self.dimension:
            log.info("Scale won't be processed: photo is to small.")
        else:
            if width_src > height_src:
                height_dest = self.dimension * height_src / width_src
                width_dest = self.dimension
            else:
                width_dest = self.dimension * width_src / height_src
                height_dest = self.dimension

            # Si on redimmensionne selon une taille paire, on force la
            # largeur et hauteur finales de l'image a etre egalement
            # paires.
            if self.dimension % 2 == 0:
                height_dest = height_dest - height_dest % 2
                width_dest = width_dest - width_dest % 2

            im=im.resize((width_dest, height_dest), Image.ANTIALIAS)
            log.info("Processed: %s" % dest)

        # save processed image
        im.save(dest, quality=self.quality)


    def remove_image(self, uri):
        """
        Remove scaled and orig images associated with the given src image
        """
        # remove scaled image
        dest = os.path.join(self.abs_scaled_dest_dir, uri)
        try:
            os.unlink(dest)
        except:
            pass
        # remove orig image
        dest = os.path.join(self.abs_orig_dest_dir, uri)
        try:
            os.unlink(dest)
        except:
            pass


    def process_image(self, src, md5sum=None):
        """
        Standard processing for the given image:
        Built the destination relative path based on image timestamp
        Copy the original image to orig dest directory
        Copy the scaled and rotated image to scaled dest directory
        Remove the original image from disk
        """
        date, dest_uri = self._date_uri(src, md5sum)
        try:
            self.copy_orig(src, dest_uri)
            self.copy_scaled(src, dest_uri)
        except Exception, e:
            # clean up if an exception occured during import
            self.remove_image(dest_uri)
            raise e
        return (date, dest_uri)


    def _date_uri(self, src, md5sum=None):
        """
        Built the destination relative path based on image timestamp
        """
        try:
            exif = self._get_exif(src)
            date = datetime.datetime.strptime(
                    exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        except:
            # TODO: return None and handle this at a higher level
            date = datetime.datetime.today()

        if not md5sum:
            md5sum = img_md5(src)
        uri = os.path.join(
            date.strftime("%Y"),
            date.strftime("%m"),
            date.strftime("%d"),
            md5sum + '.' + what(src))

        return (date, uri)


    def _get_exif(self, src):
        ret = {}
        im = Image.open(src)
        info = im._getexif()
        if info == None:
            raise Exception("can't get exif")
        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            ret[decoded] = value
        return ret


    def _check_paths(self, src, dest=None):
        """
        Checks validity of src and/or dest paths
        """
        # fail if src photo does not exist
        if isinstance(src, (StringType, UnicodeType)) and \
                not os.path.exists(src):
            log.info("Source photo does not exists: %s" % src)
            return False
        # fail if dest photo already exists
        if dest is not None and os.path.exists(dest):
            log.info("Destination photo already exists: %s" % dest)
            return False
        return True

