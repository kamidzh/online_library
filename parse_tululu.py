import requests
import os
from bs4 import BeautifulSoup	
from pathvalidate import sanitize_filename
import pathlib
from urllib.parse import urljoin, urlsplit, unquote
import argparse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(response, filename, folder='books/'):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(unquote(file_path), 'wb') as file:
        file.write(response.content)


def parse_book_page(soup):
    book_name = soup.find('div', id='content').find('h1').text.split('::')
    title = book_name[0].strip()
    author = book_name[1].strip()
    genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]
    comments = soup.find_all('div', class_="texts")
    comments_text = [comment.find('span', class_="black").text for comment in comments]
    image = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin('http://tululu.org/', image)
    book_data = {'author' : author,
                 'title' : title,
                 'genres' : genres,
                 'comments' : comments_text,
                 'image_url' : image_url}
    return book_data


def main():
    parser = argparse.ArgumentParser(
        description='Описание что делает программа'
    )
    parser.add_argument('--start_id', help='start_id', default=1, type=int)
    parser.add_argument('--end_id', help='end_id', default=10, type=int)
    args = parser.parse_args()
    for id in range(args.start_id, args.end_id):
        try:
            download_url = f"https://tululu.org/txt.php?id={id}"
            download_response = requests.get(download_url)
            download_response.raise_for_status()
            check_for_redirect(download_response)
            book_page_url = f'https://tululu.org/b{id}'
            page_response = requests.get(book_page_url)
            page_response.raise_for_status()
            soup = BeautifulSoup(page_response.text, 'lxml')
            book_data = parse_book_page(soup)
            book_title = book_data['title']
            download_txt(download_response, book_title)
            image_url = book_data['image_url']
            filename = urlsplit(image_url).path.split('/')[-1]
            download_image(image_url, filename)
        except requests.exceptions.HTTPError:
            print('такой книги нет')
        except ConnectionError:
            print('Попытка подключения к серверу')
            sleep(20)


if __name__ == '__main__':
    main()