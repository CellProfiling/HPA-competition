import os
from multiprocessing.pool import Pool
from tqdm import tqdm
import requests
import pandas as pd

def download_images(data_dir, img_list, pid, sp, ep):
    colors = ['red', 'green', 'blue', 'yellow']
    v18_url = 'http://v18.proteinatlas.org/images/'

    for i in tqdm(img_list['Id'][sp:ep], postfix=pid):  # [:5] means downloard only first 5 samples, if it works, please remove it
        img = i.split('_')
        for color in colors:
            img_path = img[0] + '/' + "_".join(img[1:]) + "_" + color + ".jpg"
            img_name = i + "_" + color + ".jpg"
            img_url = v18_url + img_path
            r = requests.get(img_url, allow_redirects=True)
            open( os.path.join(data_dir, img_name) , 'wb').write(r.content)

def run_proc(data_dir, img_list, name, sp, ep):
    print('Run child process %s (%s) sp:%d ep: %d' % (name, os.getpid(), sp, ep))
    download_images(data_dir, img_list, name, sp, ep)
    print('Run child process %s done' % (name))

def download_hpa_v18(data_dir, img_list, process_num=10):
    os.makedirs(data_dir, exist_ok=True)
    print('Parent process %s.' % os.getpid())
    list_len = len(img_list['Id'])
    p = Pool(process_num)
    for i in range(process_num):
        p.apply_async(run_proc, args=(data_dir, img_list, str(i), int(i * list_len / process_num), int((i + 1) * list_len / process_num)))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')


if __name__ == "__main__":
    img_list = pd.read_csv('https://kth.box.com/shared/static/fpqus92ep1dgfeuh6pnvg1c9ujwje4b1.csv')

    download_hpa_v18('./hpa_v18', img_list)
