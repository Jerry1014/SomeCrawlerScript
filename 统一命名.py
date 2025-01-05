from PIL import Image, ExifTags
import os


def find_all(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            if f.find('mp4') != -1 or f.find('MP4') != -1 or f.find('py') != -1:
                print(f'unsupported file {f}')
                continue
            yield root, f
        # 只遍历当前目录
        break


if __name__ == '__main__':
    # 日期-下一个图片需要（兼容多个图片日期相同的场景）
    photo_name_count_dict = dict()

    for img_root, img_file in find_all(os.getcwd()):
        origin_img_path = os.path.join(img_root, img_file)
        with (Image.open(origin_img_path) as img):
            exif_data = img.getexif()
            if exif_data and \
                    (ExifTags.Base.DateTimeOriginal in exif_data or ExifTags.Base.DateTime in exif_data
                     or ExifTags.Base.DateTimeDigitized in exif_data):
                data: str = exif_data[ExifTags.Base.DateTimeOriginal] if ExifTags.Base.DateTimeOriginal in exif_data \
                    else exif_data[ExifTags.Base.DateTime] if ExifTags.Base.DateTime in exif_data \
                    else exif_data[ExifTags.Base.DateTimeDigitized]
            else:
                print(f'cannot get date from {origin_img_path} {exif_data}')
                continue

        photo_name = data.replace(':', '').replace(' ', '_')
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
