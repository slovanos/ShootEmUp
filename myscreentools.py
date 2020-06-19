# My Screen tools

def cropRegion(coord, topCrop=0, bottomCrop=0, leftCrop=0, rightCrop=0):
    """crops a region defined by two coordinates"""

    w = coord[1][0]-coord[0][0] # x2 - x1
    h = coord[1][1]-coord[0][1] # y2 - y1
    
    y1 = coord[0][1] + topCrop * h # y1 = y1 + topCrop * h
    y2 = coord[1][1] - bottomCrop * h # y2 = y2 - bottomCrop * h
    x1 = coord[0][0] + leftCrop * w # x1 = x1 + letCrop * w
    x2 = coord[1][0] - rightCrop * w # x2 = x2 - rightCrop * w

    return [(int(x1),int(y1)),(int(x2),int(y2))]


def coord2mssroi(coord, cropRegion=False, topCrop=0, bottomCrop=0, leftCrop=0, rightCrop=0):
    """Transforms coordinates to MSS ROI format"""

    roi = {'top': coord[0][1], 'left': coord[0][0], 'width': coord[1][0]-coord[0][0], 'height': coord[1][1]-coord[0][1]}

    if cropRegion:
        roi['top'] = roi['top'] + topCrop * roi['height']
        roi['left'] = roi['left'] + leftCrop * roi['width']
        roi['width'] = roi['width'] * ( 1 - ( leftCrop + rightCrop ))
        roi['height'] = roi['height'] * (1 - (topCrop + bottomCrop))
        
    return roi


def img2ScnCoords(scnRoiCoords, imgCoords):
    """Converts the list of image-related coordinates imgCoords to absolute screen coordinates
    scnRoiCoords: The Screen coordinates describing the ROI (two points)"""

    absCoords = [(point[0]+scnRoiCoords[0][0], point[1]+scnRoiCoords[0][1]) for point in imgCoords]

    return absCoords
