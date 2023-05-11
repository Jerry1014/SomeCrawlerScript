import os
import re
import time

import requests
from fake_useragent import UserAgent

'''咪咕音乐下载类'''


class Migu:
    def __init__(self, save_dir=None, auto_download=True):
        self.auto_download = auto_download
        self.headers = {
            'Referer': 'https://m.music.migu.cn/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
        }
        self.player_url = 'https://app.pd.nf.migu.cn/MIGUM3.0/v1.0/content/sub/listenSong.do?channel=mx&copyrightId={copyrightId}&contentId={contentId}&toneFlag={toneFlag}&resourceType={resourceType}&userId=15548614588710179085069&netType=00'
        self.player_url_flac = 'https://xiaoai.sec-an.cn/play?s=migu&id={copyrightId}'
        self.search_url = 'http://pd.musicapp.migu.cn/MIGUM3.0/v1.0/content/search_all.do'
        self.params = {
            'ua': 'Android_migu',
            'version': '5.0.1',
            'text': None,
            'pageNo': '1',
            'pageSize': '3',
            'searchSwitch': '{"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":1}',
        }
        self.save_dir = save_dir if save_dir is not None else 'music'
        self.chunk_size = 1024
        self.ua = UserAgent()

        self.session = requests.Session()

    '''歌曲搜索'''

    def search(self, keyword):
        assert keyword is not None

        headers, params = self.headers.copy(), self.params.copy()
        params['text'] = keyword
        headers['User-Agent'] = self.ua.random

        response = self.session.get(self.search_url, headers=headers, params=params, timeout=2)

        result = self.parseResponse(response)
        return result

    """搜索结果解析"""

    def parseResponse(self, response):
        all_items = response.json()['songResultData']['result']
        for item in all_items:
            ext = ''
            download_url = ''
            file_size = '-MB'

            # todo flac 跟 live的特殊过滤逻辑，未来抽象一下

            for rate in sorted(item.get('rateFormats', []), key=lambda x: int(x['size']), reverse=True):
                if (int(rate['size']) == 0) or (not rate.get('formatType', '')) or (
                        not rate.get('resourceType', '')): continue
                ext = 'flac' if rate.get('formatType') == 'SQ' else 'mp3'
                if ext != 'flac':
                    download_url = self.player_url.format(
                        copyrightId=item['copyrightId'],
                        contentId=item['contentId'],
                        toneFlag=rate['formatType'],
                        resourceType=rate['resourceType'])
                else:
                    download_url = self.player_url_flac.format(copyrightId=item["copyrightId"])
                file_size = str(round(int(rate['size']) / 1024 / 1024, 2)) + 'MB'
                break

            if not download_url or ext != 'flac':
                continue

            song_name = filterBadCharacter(item.get('name', f'?{time.time()}'))
            if song_name.find('live') > -1 or song_name.find('Live') > -1:
                continue

            singers = filterBadCharacter(','.join([s.get('name', '') for s in item.get('singers', [])]))

            if not self.auto_download:
                if_download = input(f"是否下载{singers}-{song_name}(break退出 yes下载)\n")
                if if_download == 'break':
                    break
                elif if_download != 'yes':
                    continue

            song_info = {
                'songid': str(item['id']),
                'singers': singers,
                'album': filterBadCharacter(item.get('albums', [{'name': '-'}])[0].get('name', '-')),
                'songname': song_name,
                'download_url': download_url,
                'lyric_url': item.get('lyricUrl', ''),
                'filesize': file_size,
                'ext': ext,
            }
            return song_info

    '''歌曲下载'''

    def download(self, song_info):
        print(f"正在下载 >>>> {song_info['songname']}")

        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random

        touchdir(self.save_dir)
        savepath = os.path.join(self.save_dir, f"{song_info['singers']} - {song_info['songname']}.{song_info['ext']}")

        result_sign = False
        with open(savepath, 'wb') as f \
                , self.session.get(song_info['download_url'], headers=headers, stream=True, timeout=60) as response:
            if response.status_code in [200] :
                total_size = 0
                for chunk in response.iter_content(chunk_size=None):
                    if not chunk:
                        continue
                    f.write(chunk)
                    total_size += len(chunk)

                result_sign = total_size == int(response.headers['content-length'])

        if not result_sign:
            print(f"下载失败 >>>> {song_info['songname']}")
            os.remove(savepath)
        else:
            print(f"下载完成 >>>> {song_info['songname']}")
        return result_sign


'''新建文件夹'''


def touchdir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        return False
    return True


'''清除可能出问题的字符'''


def filterBadCharacter(string, fit_gbk=True):
    need_removed_strs = ['<em>', '</em>', '<', '>', '\\', '/', '?', ':', '"', '：', '|', '？', '*']
    for item in need_removed_strs:
        string = string.replace(item, '')
    try:
        rule = re.compile(u'[\U00010000-\U0010ffff]')
    except:
        rule = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    string = rule.sub('', string)
    if fit_gbk:
        string_clean = ''
        for c in string:
            try:
                c = c.encode('gbk').decode('gbk')
                string_clean += c
            except:
                continue
        string = string_clean
    return string.strip().encode('utf-8', 'ignore').decode('utf-8')
