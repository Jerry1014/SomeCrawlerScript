import threading
import time
from concurrent.futures import ThreadPoolExecutor

from migu_core import Migu

cur_index = 0
lock = threading.Lock()
pool = ThreadPoolExecutor(max_workers=1)
migu = Migu(auto_download=False)


def action(song_name):
    download_result = False
    try:
        search_result = migu.search(song_name)
        if search_result:
            retry_count = 3
            while retry_count > 0:
                try:
                    download_result = migu.download(search_result)
                    break
                except:
                    retry_count -= 1
                    pass
    except:
        pass

    return song_name if not download_result else None


download_future_list = []
fail_song_list = set()
with open('song_list.txt', encoding='utf-8') as f:
    for line in f.readlines():
        song_name = line.rstrip()
        download_future_list.append(pool.submit(action, song_name))

    total_count = len(download_future_list)
    while download_future_list:
        new_list = []
        for future in download_future_list:
            if future.done():
                if future.result() is not None:
                    fail_song_list.add(future.result())
            else:
                new_list.append(future)
        download_future_list = new_list

        print(f'{total_count - len(download_future_list)} / {total_count}')
        time.sleep(10)
pool.shutdown()

print(fail_song_list)