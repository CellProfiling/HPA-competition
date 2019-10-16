"""Download HPAv18 dataset."""
import os
from multiprocessing.pool import Pool

import pandas as pd
import requests
from tqdm import tqdm


def download_images(data_dir, img_list, pid, start_idx, end_idx):
    """Download HPAv18 images."""
    colors = ["red", "green", "blue", "yellow"]
    v18_url = "http://v18.proteinatlas.org/images/"

    for i in tqdm(img_list["Id"][start_idx:end_idx], postfix=pid):
        img = i.split("_")
        for color in colors:
            img_path = img[0] + "/" + "_".join(img[1:]) + "_" + color + ".jpg"
            img_name = i + "_" + color + ".jpg"
            img_url = v18_url + img_path
            response = requests.get(img_url, allow_redirects=True)
            open(os.path.join(data_dir, img_name), "wb").write(response.content)


def run_proc(data_dir, img_list, name, start_idx, end_idx):
    """Handle one mp process."""
    print(
        "Run child process %s (%s) start:%d end: %d"
        % (name, os.getpid(), start_idx, end_idx)
    )
    download_images(data_dir, img_list, name, start_idx, end_idx)
    print("Run child process %s done" % (name))


def download_hpa_v18(data_dir, img_list, process_num=10):
    """Download HPAv18 images with a multiprocessing pool."""
    os.makedirs(data_dir, exist_ok=True)
    print("Parent process %s." % os.getpid())
    list_len = len(img_list["Id"])
    pool = Pool(process_num)
    for i in range(process_num):
        pool.apply_async(
            run_proc,
            args=(
                data_dir,
                img_list,
                str(i),
                int(i * list_len / process_num),
                int((i + 1) * list_len / process_num),
            ),
        )
    print("Waiting for all subprocesses done...")
    pool.close()
    pool.join()
    print("All subprocesses done.")


def main():
    """Run main entrypoint."""
    img_list = pd.read_csv(
        "https://kth.box.com/shared/static/fpqus92ep1dgfeuh6pnvg1c9ujwje4b1.csv"
    )

    download_hpa_v18("./hpa_v18", img_list)


if __name__ == "__main__":
    main()
