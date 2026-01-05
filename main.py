import os
from course_parser import parse_course_page
from downloader import download_video

COURSE_URL = "https://www.cs.utexas.edu/~risto/cs378ne/private/reading.html"
OUTPUT_DIR = "videos"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    course_items = parse_course_page(COURSE_URL)

    total = len(course_items)
    print(f"Prepare to download {total} videos.")

    for index, item in enumerate(course_items, 1):
        print(f"Progress ({index}/{total}): {item['title']}")
        download_video(video_url=item['url'], title=item['title'], output_dir=OUTPUT_DIR)

if __name__ == "__main__":
    main()
