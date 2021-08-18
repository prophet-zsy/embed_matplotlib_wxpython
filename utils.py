import cv2, threading
from matplotlib.pyplot import margins
from six import with_metaclass

 
class StoppableThread(threading.Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()
        self._stop_event.clear()

    def stop(self):
        self._stop_event.set()
 
    def stopped(self):
        return self._stop_event.is_set()

    def tell_start(self):
        self._stop_event.clear()


def get_img_from_video(video_path, frame_num):
    videoCapture = cv2.VideoCapture(video_path)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
            int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fNUMS = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    assert frame_num < fNUMS, "you must get the frame whose num is less than {}, but you give frame_id {}".format(fNUMS, frame_num)
    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, float(frame_num))
    success, frame = videoCapture.read()
    videoCapture.release()
    if not success:
        raise Exception("get the img from the video failed!")
    return frame, fNUMS
 
def read_data(data_path):
    with open(data_path, 'r') as f:
        content = f.readlines()
        x = []
        y = []
        for item in content:
            x.append(int(item.split(",")[0]))
            y.append(float(item.split(",")[1]))
    return x, y


if __name__ == '__main__':
    video_path = "./data/A.mp4"
    frame_num = 433
    frame, fNUMS = get_img_from_video(video_path, frame_num)
    cv2.imshow("frame", frame)
    cv2.waitKey(0)