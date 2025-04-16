import os
import time

from PIL import Image, ExifTags


def find_all(pic_dir: str):
    for root, ds, fs in os.walk(pic_dir):
        for f in fs:
            if f.find('mp4') != -1 or f.find('MP4') != -1 or f.find('py') != -1:
                print(f'unsupported file {f}')
                continue
            yield root, f
        # 只遍历当前目录
        break


def do_rename(img_root: str, img_file: str) -> None:
    origin_img_path = os.path.join(img_root, img_file)
    photo_name = None

    with (Image.open(origin_img_path) as img):
        exif_data = img.getexif()
        if exif_data and \
                (ExifTags.Base.DateTimeOriginal in exif_data or ExifTags.Base.DateTime in exif_data
                 or ExifTags.Base.DateTimeDigitized in exif_data):
            data: str = exif_data[ExifTags.Base.DateTimeOriginal] if ExifTags.Base.DateTimeOriginal in exif_data \
                else exif_data[ExifTags.Base.DateTime] if ExifTags.Base.DateTime in exif_data \
                else exif_data[ExifTags.Base.DateTimeDigitized]
            photo_name = data.replace(':', '').replace(' ', '_')
        else:
            # 时间戳
            img_file_name = img_file.split('.')[0]
            if img_file_name.isdigit() and (len(img_file_name) == 13 or len(img_file_name) == 10):
                timestamp = int(img_file_name) / 1000 if len(img_file_name) == 13 else int(img_file_name)
                photo_name = time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))
            else:
                print(f'cannot get date from {origin_img_path} {exif_data}')
                return

    if photo_name in photo_name_count_dict:
        cur_count = photo_name_count_dict[photo_name]
        photo_name_count_dict[photo_name] += 1
        photo_name = photo_name + '_' + str(cur_count)
    else:
        photo_name_count_dict[photo_name] = 1
    new_file_name = photo_name + '.' + img_file.split('.')[-1]
    # print(f'{data} {new_file_name}')

    target_img_path = os.path.join(img_root, new_file_name)
    if target_img_path != origin_img_path:
        if os.path.exists(target_img_path):
            print(f'file has exist. {origin_img_path} {target_img_path}')
        else:
            os.rename(origin_img_path, target_img_path)


if __name__ == '__main__':
    # 日期-下一个图片需要（兼容多个图片日期相同的场景）
    photo_name_count_dict = dict()

    for root, file in find_all(os.getcwd()):
        try:
            do_rename(root, file)
        except Exception as e:
            print(repr(e))
