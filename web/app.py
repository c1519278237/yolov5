import detect
from flask import Flask, request, jsonify, send_file, Response, stream_with_context, current_app, after_this_request
import os
from flask_cors import CORS
# 设置日志的记录等级
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

import service

app = Flask('app')
cors = CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG)
# 定义允许上传的文件类型
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VIDEO_EXTENSIONS = {'mp4'}


# 判断文件类型是否允许上传
def is_image(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS


def is_video(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in VIDEO_EXTENSIONS


def get_file_type(filename):
    if is_image(filename):
        return "image"
    elif is_video(filename):
        return "video"
    else:
        return None


@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否上传了文件
    if 'file' not in request.files:
        return jsonify({'code': '10001', 'error': '未上传文件!'})

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'code': '10002', 'error': '未选择文件!'})

    file_type = get_file_type(file.filename)
    # 检查文件类型是否允许上传
    if file_type is None:
        return jsonify({'code': '10003', 'error': "文件类型不允许!只支持'png', 'jpg', 'jpeg', 'mp4'"})

    logging.info("文件名" + file.filename + ",文件类型:" + file_type)

    # 保存上传的文件到本地
    filename = file.filename
    file.save(filename)

    # 进行识别
    result_path = detect.do_recognition('web/' + filename)
    if len(os.listdir(result_path)) == 0:
        return jsonify({'code': '10004', 'error': "生成失败!"})
    # 获取第一个文件的文件名,暂不支持批量返回
    result_path = os.path.join(result_path, os.listdir(result_path)[0])
    logging.info("识别结果保存到" + result_path)
    # 删除原文件
    os.remove(filename)

    # 如果是视频,上传到阿里云vod
    if file_type == "video":
        service.play_video(result_path)

    return result_path


@app.route('/image')
def get_image():
    path = request.args['path']
    return send_file(path, mimetype='image/gif')


@app.route('/openMonitor', methods=['POST'])
def open_monitor():
    detect.open_monitor()
    return Response("开启成功")


@app.route('/closeMonitor', methods=['POST'])
def close_monitor():
    video_dir = detect.close_monitor()
    video_path = os.path.join(video_dir, "0.mp4")
    service.play_video(video_path)
    return video_path


@app.route('/video')
def get_video():
    path = request.args['path']
    # 打开视频文件
    video_file = open(path, "rb")
    # 使用stream_with_context函数将文件作为流返回
    return Response(stream_with_context(video_file), mimetype='video/mp4')
    # return send_file(path, mimetype='video/mp4')


@app.route('/hello')
def hello():
    return "可以访问!"


@app.errorhandler(Exception)
def framework_error(e):
    logger = current_app.logger

    if isinstance(e, HTTPException):
        # 比如404
        logger.error("HTTPException")
        logger.exception(e)
        return jsonify({'code': '10000', 'error': '服务器内部错误!'})
    else:
        # 非http的运行时异常,比如10/0
        logger.error("其他严重错误!")
        logger.exception(e)
        return jsonify({'code': '10000', 'error': '服务器内部错误!'})


if __name__ == '__main__':
    app.run(debug=True)
