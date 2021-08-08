# 读取并展示A.mp4的视频
import cv2

video_path = "A.mp4"
videoCapture = cv2.VideoCapture(video_path)

fps = videoCapture.get(cv2.CAP_PROP_FPS)
size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
        int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fNUMS = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
print(fNUMS)
success, frame = videoCapture.read()
cv2.imshow('windows', frame) #显示
cv2.waitKey(0) #延迟
while success:
    cv2.imshow('windows', frame) #显示
    cv2.waitKey(int(1000/int(fps))) #延迟
    success, frame = videoCapture.read() #获取下一帧
 
videoCapture.release()

# 生成A.txt文件的数据
import random

data_path = "./A.txt"
fNUMS = 568
with open(data_path, "w") as f:
    data = []
    for i in range(fNUMS):
        data.append(random.random())
    for idx, da in enumerate(data):
        f.write("{},{}\n".format(idx, da))
