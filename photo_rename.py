import os
import re
import time

import exifread


def find_all_img(target_dir: str):
    for target_dir, ds, fs in os.walk(target_dir):
        for file_path in fs:
            if file_path.find('mp4') != -1 or file_path.find('MP4') != -1 or file_path.find('py') != -1:
                print(f'unsupported file {file_path}')
                continue
            yield target_dir, file_path
        # 只遍历当前目录
        break


def do_rename(img_dir: str, img_file_path: str) -> None:
    origin_img_path = os.path.join(img_dir, img_file_path)
    photo_name = get_photo_name_by_exif(origin_img_path)

    # 同秒内拍摄的命名冲突
    if photo_name in photo_name_count_dict:
        cur_count = photo_name_count_dict[photo_name]
        photo_name_count_dict[photo_name] += 1
        photo_name = photo_name + '_' + str(cur_count)
    else:
        photo_name_count_dict[photo_name] = 1
    new_file_name = photo_name + '.' + img_file_path.split('.')[-1]

    # 重命名
    target_img_path = os.path.join(img_dir, new_file_name)
    if target_img_path != origin_img_path:
        if os.path.exists(target_img_path):
            print(f'file has exist. {origin_img_path} {target_img_path}')
        else:
            os.rename(origin_img_path, target_img_path)


def get_photo_name_by_exif(origin_img_path):
    # 读取exif信息
    shooting_time = None
    with open(origin_img_path, "rb") as f:
        tags = exifread.process_file(f)
        for tag, value in tags.items():
            if re.match('Image DateTime', tag):
                # 2025:09:21 16:49:59
                tem = str(value)
                shooting_time = tem.replace(':', '').replace(' ', '_')
                break

    # exif中没有时，尝试从文件名获取
    if shooting_time is None:
        # 时间戳
        img_file_name = os.path.split(origin_img_path)[-1].split('.')[0]
        if img_file_name.isdigit() and (len(img_file_name) == 13 or len(img_file_name) == 10):
            timestamp = int(img_file_name) / 1000 if len(img_file_name) == 13 else int(img_file_name)
            shooting_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))
        else:
            raise Exception(f'cannot get date from {origin_img_path}')

    return shooting_time


if __name__ == '__main__':
    # 日期-下一个图片需要（兼容多个图片日期相同的场景）
    photo_name_count_dict = dict()

    for dir, file_path in find_all_img(os.getcwd()):
        try:
            do_rename(dir, file_path)
        except Exception as e:
            print(e)
