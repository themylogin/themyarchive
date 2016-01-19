# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import os
import re
import subprocess

from themyutils.requests import chrome

from themyarchive.worker.variant_task import variant_task

logger = logging.getLogger(__name__)

__all__ = [b"google_chrome_screenshot"]


@variant_task
def wget(variant, fs_archive_path):
    stdout, stderr = subprocess.Popen(["wget", "-p", "-k", "-H",
                                       "-e", "robots=off",
                                       "-U", chrome,
                                       "-P", fs_archive_path,
                                       "-T", "30",
                                       "--restrict-file-names=ascii",
                                       variant.url.url],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT).communicate()
    saving_to = re.search(r"Saving to: (.+)", stdout).group(1).decode("utf-8")[1:-1]
    return {"relpath": os.path.relpath(saving_to, fs_archive_path)}
