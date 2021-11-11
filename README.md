# Install

**Chrome version 95 is required to execute the crawler.**

Install it in a virtual environment.

```
git clone https://github.com/hjk1996/instagram-image-crawler.git
cd instagram-image-crawler
pip install -r requirements.txt
```

# Crawling

## 1. Set ID and password

Set the ID and password of the Instagram account to be used for crawling in config.env.

![image](https://user-images.githubusercontent.com/82424229/141061835-73f78b9b-e783-4aad-bd86-ff91304fe49f.png)


## 2. Run

--tag: The tag of the image you want to collect.

--n_imgs: The number of images you want to collect.

--headless(optional): If the value is True, crawling is performed in headless mode.

```
python main.py --tag chicken --n_imgs 100
  ```

## Images

Images are stored in a folder of tag names in the images folder.
