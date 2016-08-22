# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from docker import Client
import functools
import logging
import os
import pipes
import shutil
import subprocess
import tempfile
import time

from themyarchive.app import app
from themyarchive.worker.variant_task import variant_task

logger = logging.getLogger(__name__)

__all__ = [b"google_chrome"]


@variant_task
def google_chrome(variant, fs_archive_path):
    fs_screenshot_path = os.path.join(fs_archive_path, "screenshot.png")
    fs_pdf_path = os.path.join(fs_archive_path, "page.pdf")

    return take_screenshot(variant.url.url, variant.data["width"], variant.data["height"],
                          fs_screenshot_path, fs_archive_path, fs_pdf_path)


def take_screenshot(url, width, height, screenshot_path, html_path, pdf_path):
    docker = Client(base_url="unix://run/docker.sock")

    container = docker.create_container(
        image="themyarchive_chrome",
        # http://csmarosi.github.io/sigbus.html
        volumes=["/dev/shm", "/run/shm"],
        host_config=docker.create_host_config(binds=[
            "/dev/shm:/dev/shm",
            "/run/shm:/run/shm",
        ])
    )["Id"]
    docker.start(container)

    try:
        run_command = functools.partial(docker_container_run_command, docker, container)

        docker.put_archive(container, "/home", open(app.config["CHROME_PATH"]))
        run_command(["chown", "-R", "chrome:chrome", "/home/chrome"])

        run_command(["/usr/bin/Xvfb", ":0", "-screen", "0", "%dx%dx24" % (width, height)],
                    user="chrome", detach=True)
        time.sleep(5)

        run_command(["/bin/bash", "-c", "DISPLAY=:0 openbox-session"],
                    user="chrome", detach=True)
        time.sleep(5)

        run_command(["/bin/bash", "-c", "DISPLAY=:0 google-chrome --no-sandbox %s" % pipes.quote(url).encode("utf-8")],
                    user="chrome", detach=True)
        time.sleep(120)

        xdotool = lambda cmds: [(run_command(["/bin/bash", "-c", "DISPLAY=:0 xdotool %s" % cmd], user="chrome"),
                                 time.sleep(1))
                                for cmd in cmds]
        xdotool(["mousemove %d %d" % (width - 48, 43),
                 "click 1"])
        time.sleep(60)

        xdotool(["keydown ctrl",
                 "key s",
                 "keyup ctrl",
                 "key p",
                 "key a",
                 "key g",
                 "key e",
                 "key period",
                 "key p",
                 "key n",
                 "key g",
                 "key Return"])
        time.sleep(5)

        xdotool(["keydown ctrl",
                 "key w",
                 "keyup ctrl"])

        xdotool(["keydown ctrl",
                 "key s",
                 "keyup ctrl",
                 "key p",
                 "key a",
                 "key g",
                 "key e",
                 "key period",
                 "key h",
                 "key t",
                 "key m",
                 "key l",
                 "key Return"])
        time.sleep(60)

        xdotool(["keydown ctrl",
                 "key p",
                 "keyup ctrl",
                 "key Return",
                 "keydown shift",
                 "key d",
                 "keyup shift",
                 "key o",
                 "key w",
                 "key n",
                 "key l",
                 "key o",
                 "key a",
                 "key d",
                 "key s",
                 "key slash",
                 "key p",
                 "key a",
                 "key g",
                 "key e",
                 "key period",
                 "key p",
                 "key d",
                 "key f",
                 "key Return"])
        time.sleep(10)

        with tempfile.NamedTemporaryFile(suffix=".tar") as f:
            f.write(docker.get_archive(container, "/home/chrome/Downloads")[0].read())
            f.flush()

            tmp_dir = tempfile.mkdtemp()
            try:
                subprocess.check_call(["tar", "xf", f.name, "-C", tmp_dir])
                downloads = os.path.join(tmp_dir, "Downloads")
                files = os.listdir(downloads)
                logger.info("Files: %r", files)

                features = []

                screenshot = filter(lambda name: name.endswith(".png"), files)[0]
                shutil.move(os.path.join(downloads, screenshot), screenshot_path)
                files.remove(screenshot)

                pdf = filter(lambda name: name.endswith(".pdf"), files)[0]
                shutil.move(os.path.join(downloads, pdf), pdf_path)
                files.remove(pdf)

                try:
                    data_dir = filter(lambda name: os.path.isdir(os.path.join(downloads, name)), files)[0]
                except IndexError:
                    pass
                else:
                    shutil.move(os.path.join(downloads, data_dir), html_path)
                    files.remove(data_dir)

                if len(files):
                    shutil.move(os.path.join(downloads, files[0]), os.path.join(html_path, "index.html"))
                    features.append("html")

                os.chmod(screenshot_path, 0644)
                os.chmod(html_path, 0755)
                for root, dirs, files in os.walk(html_path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0755)
                    for fl in files:
                        os.chmod(os.path.join(root, fl), 0644)
            finally:
                shutil.rmtree(tmp_dir)
    finally:
        docker.remove_container(container, force=True)

    return {"features": features}


def docker_container_run_command(docker, container, command, user="root", detach=False):
    docker.exec_start(docker.exec_create(container, command, user=user)["Id"], detach=detach)
