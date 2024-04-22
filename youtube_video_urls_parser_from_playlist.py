from pytube import Playlist
import sqlite3


def insert_one(youtube_video: str) -> None:
    '''
    Вставка единичной ссылки
    Если ссылка попала в этот метод, значит это свежий (не просмотренный) контент.
    Значение поля is_new в таблице автоматически == 1 (True)
    '''
    conn = sqlite3.connect('youtube.db')
    cur = conn.cursor()
    youtube_video = 'https://www.youtube.com/watch?v=k1aDVWL_ytY'
    cur.execute("INSERT INTO youtube_video_urls(youtube_video_url) VALUES (?)",  (youtube_video))
    conn.commit()

def insert_many(youtube_video_urls: list) -> None:
    '''
    Вставка списка ссылок
    Если ссылка в списке, который попал в этот метод, значит это свежий (не просмотренный) контент.
    Значение поля is_new в таблице автоматически == 1 (True)
    '''
    conn = sqlite3.connect('youtube.db')
    cur = conn.cursor()
    cur.executemany("INSERT INTO youtube_video_urls (youtube_video_url) VALUES (?)",  (youtube_video_urls))
    conn.commit()

def is_exists(youtube_video_url: str) -> bool:
    '''
    Проверка ссылки на видео по базе
    '''
    db = 'youtube.db'
    conn = sqlite3.connect(db)
    with conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM youtube_video_urls;''')
        youtube_video_urls = cursor.fetchall()
        for youtube_video_url in youtube_video_urls:
            pass




def get_youtube_videos_from_playlist(youtube_playlist_url):
    '''
    Библиотека для работы с youtube
    https://pytube.io/en/latest/index.html - sync docs
    # попробовать асинхронный вариант (в данный момент эта библиотека не работает):
    #python -m pip install git+https://github.com/msemple1111/pytube
    Просто вставляем в базу все позиции, которых еще нет
    '''

    p = Playlist(youtube_playlist_url) # тут искаропки допускается ссылка с параметром видоса внутри!


    for video in p.videos:
        '''
        temp_list = []
        temp_list.append(video.watch_url)
        youtube_video_urls.append(temp_list)
        insert_many(youtube_video_urls)
        '''
        conn = sqlite3.connect('youtube.db')
        cur = conn.cursor()
        #youtube_video = 'https://www.youtube.com/watch?v=k1aDVWL_ytY'
        print(type(video.watch_url), video.watch_url)
        cur.execute("INSERT OR IGNORE INTO youtube_video_urls(youtube_video_url) VALUES (?);", (video.watch_url,))
        #cur.execute("INSERT OR IGNORE INTO youtube_video_urls(youtube_video_url) VALUES (?);", (youtube_video))
        #last_row_id = cur.execute("SELECT youtube_video_url FROM youtube_video_urls WHERE youtube_video_url = ?;" (video.watch_url, ))
        conn.commit()
    #return last_row_id
    
if __name__ == '__main__':
    # test insert many
    '''
    youtube_video_urls = [
        ['https://www.youtube.com/watch?v=k1aDVWL_ytY'],
        ['https://www.youtube.com/watch?v=2xeSuRx1vnU'],
        ['https://www.youtube.com/watch?v=gvtUzd2PcDk'],
    ]
    insert_many(youtube_video_urls)
    '''
    # test insert one
    '''
    youtube_video_url = 'https://www.youtube.com/watch?v=g1eKfEIQ2oc'
    insert_one(youtube_video_url)
    '''
    # test get_youtube_videos_from_playlist
    
    youtube_playlist_url='https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e'
    get_youtube_videos_from_playlist(youtube_playlist_url)
    