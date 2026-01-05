# Box 视频下载器

# Box Video Downloader

有一些视频是存在一个叫 [Box](https://www.box.com/) 的云盘服务上的，比如我关心的这个 [UT Austin CS378 Neuroevolution](https://www.cs.utexas.edu/~risto/cs378ne/private/reading.html) 的课程，于是我写了一个从 Box 爬取视频的小脚本。

Some videos are hosted on a cloud storage service called [Box](https://www.box.com/). For example, the [UT Austin CS378 Neuroevolution](https://www.cs.utexas.edu/~risto/cs378ne/private/reading.html) course I am interested in. So I wrote a small script to crawl videos from Box.

## 依赖

## Dependencies

依赖可见`requirements.txt`。

Dependencies are listed in `requirements.txt`.

```bash
pip install requests beautifulsoup4 imageio-ffmpeg
```

## 使用方法

## Usage

`main.py`的功能是下载需要的 [UT Austin CS378 Neuroevolution](https://www.cs.utexas.edu/~risto/cs378ne/private/reading.html) 课程的视频。直接运行即可。


The function of `main.py` is to download the videos for the [UT Austin CS378 Neuroevolution](https://www.cs.utexas.edu/~risto/cs378ne/private/reading.html) course. Just run it directly.

```bash
python main.py
```

当然，如果你想下载 Box 上的其他视频，可以调用`downloader.py`中的`download_video`函数，传入视频的 URL 和标题即可。比如下面这个示例：

Of course, if you want to download other videos from Box, you can call the `download_video` function in `downloader.py`, passing in the video URL and title. For example:

```python
from downloader import download_video

download_video(video_url="https://utexas.app.box.com/s/7jw2z3c2l5521xdz5uvs3m912shbq9ty", title="Introduction to Neuroevolution", output_dir="videos")

```

## 技术原理

## Technical Details

也没什么技术原理，大概就是先去伪造游客登录的cookie，签名之类的东西，然后把一个视频的所有分块爬下来，这个视频的请求逻辑和哔哩哔哩很像，都是分块请求并且把视频和音频分开，只需要把它们拼起来就行了。

There isn't much deep technology involved. It roughly involves forging guest login cookies, signatures, and so on, then crawling all chunks of a video. The request logic for these videos is very similar to Bilibili, using chunked requests and separating video and audio streams, which then just need to be merged together.
