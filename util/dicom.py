import os
import pydicom
import numpy as np

def load_dicom(file, center=None, width=None, raw=False):
    """
    load dicom file and return pixels and position in a dict.
    """
    with pydicom.read_file(file) as dcm:
        if center == None:
            if isinstance(dcm.WindowCenter, pydicom.multival.MultiValue):
                center = dcm.WindowCenter[0]
            else:
                center = dcm.WindowCenter
        if width == None:
            if isinstance(dcm.WindowWidth, pydicom.multival.MultiValue):
                width = dcm.WindowWidth[0]
            else:
                width = dcm.WindowWidth
        min_val = center - width / 2
        max_val = center + width / 2
        pixels = dcm.pixel_array * dcm.RescaleSlope + dcm.RescaleIntercept
        if not raw:
            pixels[pixels < min_val] = min_val
            pixels[pixels > max_val] = max_val
    return {
        'pixels': pixels,
        'pixel_size': list(map(float, [dcm.SliceThickness] + list(dcm.PixelSpacing))),
        'position': dcm.InstanceNumber
    }

def load_dicom_volume(dirname, pixel_size=False):
    """
    load dicom directory and convert it into 3d-numpy-array with order
    [height, length, width].
    """
    dcms = []
    for dirPath, dirNames, fileNames in os.walk(dirname):
        for f in fileNames:
            in_file = os.path.join(dirPath, f)
            img = load_dicom(in_file)
            dcms.append((img['position'], img['pixels']))

    volume = [pixels for (position, pixels) in sorted(dcms, key=lambda dcm: dcm[0])]

    ret = np.asarray(volume)

    if pixel_size:
        ret = (ret, img['pixel_size'])

    return ret
