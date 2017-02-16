import requests
from lxml import html
import sys
import os
print("Bookworm...")
url = "http://www.allitebooks.com/"
base = requests.get(url)
base_tree = html.fromstring(base.content)
last_num = base_tree.xpath("//*[@id=\"main-content\"]/div/div/a[5]")

page_struct = "page/"
numbers = range(1, int(last_num[0].text))

for number in numbers:
    pdf_url = url + page_struct + str(number)
    r = requests.get(pdf_url)
    tree = html.fromstring(r.content)
    pdflist = tree.xpath("//article/div[2]/header/h2/a")

    for article in pdflist:
        r2 = requests.get(article.attrib['href'])
        tree2 = html.fromstring(r2.content)
        elm = tree2.xpath("//*[@id=\"main-content\"]/div/article/footer/div/span[1]/a")
        down_url = elm[0].attrib['href']
        category = tree2.xpath("//*[@id=\"main-content\"]/div/article/header/div/div[2]/dl/dd[8]/a")
        local_filename = down_url.split('/')[-1]
        file_path = os.path.join(category[0].text, local_filename)

        os.makedirs(category[0].text, exist_ok=True)

        if(os.path.exists(file_path)):
            continue

        # NOTE the stream=True parameter
        r3 = requests.get(down_url, stream=True)
        with open(file_path, 'wb') as f:

            data_length = r3.headers.get('content-length')
            if data_length is None:  # no content length header
                f.write(r3.content)
            else:
                dl = 0
                total_length = int(data_length)
                for chunk in r3.iter_content(chunk_size=1024):
                    dl += len(chunk)
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                        sys.stdout.flush()

                        #f.flush() commented by recommendation from J.F.Sebastian
        print(file_path + " % page>" + str(number) )
