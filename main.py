import argparse
import time

from crawler import Crawler


def main(tag: str, n_imgs: int, headless: bool) -> None:
    c = Crawler(headless)
    c.login()
    c.search_tag(tag)
    image_urls = c.get_image_urls(n_imgs)
    c.destroy_driver()
    images = c.get_images(image_urls)
    c.save_images(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, type=str)
    parser.add_argument("--n_imgs", required=True, type=int)
    parser.add_argument("--headless", required=False, type=bool, default=False)
    args = parser.parse_args()
    

    start = time.perf_counter()
    main(args.tag, args.n_imgs, args.headless)
    duration = time.perf_counter() - start
    print(f"Crawling ended in {duration} seconds")
