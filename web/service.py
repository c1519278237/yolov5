import requests
import os


def upload_video(video_path):
    """向java服务器发起文件上传请求,上传到阿里云vod,上传成功返回videoId"""
    url = 'http://localhost:5001/video/uploadAlyVideo'
    with open(video_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        data = response.json()
    try:
        if data and data['code'] == 20000:
            print('上传成功')
            return data['data']['videoId']
        else:
            print('上传失败')
            raise Exception("上传失败!", response.text)
    finally:
        pass
        # os.remove(video_path)


def get_play_auth(video_id):
    url = 'http://localhost:5001/video/getPlayAuth/' + video_id
    response = requests.get(url)
    data = response.json()
    if data and data['code'] == 20000:
        print('获取播放凭证成功!')
        return data['data']['playAuth']
    else:
        print('获取播放凭证失败1')
        raise Exception("获取播放凭证失败!", response.text)


def play_video(relative_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.startfile(os.path.join(base_dir,'web', relative_path))


def close_sys_monitor():
    import cv2 as cv
    cap = cv.VideoCapture(0)
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    # video_id = upload_video("video/trailer.mp4")
    # print(video_id)
    # auth = get_play_auth(video_id)
    # print(auth)
    play_video('..\\runs\\detect\\exp15\\0.mp4')
