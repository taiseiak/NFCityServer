"""
This file holds the power to process images and see what
the license plate number is.

Based off the PyALPR by lukeagabric

https://github.com/lukagabric/PyALPR/blob/master/PyALPR.py
"""
import requests
import shutil
import json
import shlex
import subprocess
from PIL import Image

LOT_IP = {
    1: "NEED IP FOR THE RASPBERRY PI"
}
TEMP_IMAGE = "./Test-plate.jpg"


class PlateReader:

    def __init__(self):
        # alpr subprocess args
        alpr_command = "alpr -c eu -t hr -n 300 -j alpr.jpg"
        self.alpr_command_args = shlex.split(alpr_command)

    def alpr_subprocess(self):
        return subprocess.Popen(self.alpr_command_args, stdout=subprocess.PIPE)

    def alpr_json_results(self):
        alpr_out, alpr_error = self.alpr_subprocess().communicate()

        if not alpr_error is None:
            return None, alpr_error
        elif "No license plates found." in alpr_out:
            return None, None

        try:
            return json.loads(alpr_out), None
        except ValueError as e:
            return None, e

    def read_plate(self):
        alpr_json, alpr_error = self.alpr_json_results()

        if not alpr_error is None:
            return ""

        if alpr_json is None:
            return ""

        results = alpr_json["results"]

        for result in results:
            candidates = result["candidates"]

            for candidate in candidates:
                if candidate["matches_template"] == 1:
                    return candidate["plate"]


def check_car(lot):
    """Requests the image from the raspberry pi and process it

    Args:
        lot: int that is linked to a Raspberry Pi

    Returns:
        a tuple of the license plate number string. If the license plate
        does not exists, then it returns an empty string.


    FOR NOW, WHEN THE LOT IS 0, THEN THE FUNCTION RETURNS THE NUMBER
    FROM THE TEST IMAGE
    """
    if lot:
        """
        r = requests.get(settings.STATICMAP_URL.format(**data), stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f"""
    else:
        _write_img_as_alpr(TEMP_IMAGE)

    # Process and return
    plate_reader = PlateReader()
    return plate_reader.read_plate()


def _write_img_as_alpr(img):
    """Writes the image sent in as alpr.jpg

    Args:
        img: jpg image path
    """
    image = Image.open(img)
    temp = image.copy()
    temp.save("alpr.jpg")


def _get_plate_number():
    """Gets the plate number from a jpg image

    Returns:
        plate number (int)
    """
    plate_reader = PlateReader()
    return plate_reader.read_plate()
