__author__ = "vfdev"

# Python
import argparse
import os, sys
import shutil
import subprocess
import json

import cv2


class Video2Frames:

    def convert(self, inpput, output, maxframes):

        if not os.path.exists(input):
            parser.error("Input video file is not found")
            return 1

        if os.path.exists(output):
            shutil.rmtree(output)

        os.makedirs(args.output)

        cap = cv2.VideoCapture()
        cap.open(input)
        if not cap.isOpened():
            parser.error("Failed to open input video")
            return 1

        frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        skipDelta = 0
        if maxframes and frameCount > maxframes:
            skipDelta = frameCount / maxframes

        frameId = 0
        rotateAngle = 0
        if rotateAngle > 0 and args.verbose:
            print("Rotate output frames on {deg} clock-wise".format(deg=rotateAngle))

        exif_model = None

        while frameId < frameCount:
            ret, frame = cap.read()
            # print frameId, ret, frame.shape
            if not ret:
                print("Failed to get the frame {f}".format(f=frameId))
                continue

            # Rotate if needed:
            if rotateAngle > 0:
                if rotateAngle == 90:
                    frame = cv2.transpose(frame)
                    frame = cv2.flip(frame, 1)
                elif rotateAngle == 180:
                    frame = cv2.flip(frame, -1)
                elif rotateAngle == 270:
                    frame = cv2.transpose(frame)
                    frame = cv2.flip(frame, 0)

            fname = "frame_" + str(frameId) + ".jpg"
            ofname = os.path.join(output, fname)
            ret = cv2.imwrite(ofname, frame)
            if not ret:
                print("Failed to write the frame {f}".format(f=frameId))
                continue

            frameId += int(1 + skipDelta)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frameId)

        if exif_model:
            fields = ["Model", "Make", "FocalLength"]
            if not self.write_exif_model(os.path.abspath(output), exif_model, fields):
                print("Failed to write tags to the frames")
            # check on the first file
            fname = os.path.join(os.path.abspath(output), "frame_0.jpg")
            cmd = ["exiftool", "-j", fname]
            for field in fields:
                cmd.append("-" + field)
            ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = ret.communicate()

            result = json.loads(out)[0]
            for field in fields:
                if field not in result:
                    parser.error("Exif model is not written to the output frames")
                    return 3
        return 0

    def write_exif_model(self, folder_path, model, fields=None):
        cmd = ["exiftool", "-overwrite_original", "-r"]
        for field in fields:
            if field in model:
                cmd.append("-" + field + "=" + model[field])
        cmd.append(folder_path)
        ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ret.communicate()
        return ret.returncode == 0 and len(err) == 0
