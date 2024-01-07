import cv2, numpy

def createCapture(cameraNum: int = 0, frameWidth: float = None, frameHeight: float = None, frameRate: float = None) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(cameraNum)
    if frameWidth != None: capture.set(cv2.CV_CAP_PROP_FRAME_WIDTH, int(frameWidth))
    if frameHeight != None: capture.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, int(frameHeight))
    if frameRate != None: capture.set(cv2.CAP_PROP_FPS, int(frameRate))
    if not capture.isOpened(): raise Exception("No camera found or cannot be opened.")
    return capture

def createWriter(capture: cv2.VideoCapture, fileName: str) -> cv2.VideoWriter:
    frameWidth = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameRate = int(capture.get(cv2.CAP_PROP_FPS))
    fileName = fileName
    writer = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(*"H264"), frameRate, (frameWidth, frameHeight))
    print("Writer created at", fileName, "with", frameWidth, "*", frameHeight, frameRate, "fps")
    return writer

def saveFrameToPhoto(frame: numpy.array, savePhotoName: str):
    cv2.imwrite(savePhotoName, frame)

def saveFrameToMovie(frame: numpy.array, writer: cv2.VideoWriter):
    writer.write(frame)

def showFrame(title: str, frame: numpy.array) -> bool:
    cv2.imshow(title, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyWindow(title)
        cv2.waitKey(1)
        return False
    return True