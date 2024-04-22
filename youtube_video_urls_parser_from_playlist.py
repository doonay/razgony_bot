from pytube import Playlist

#https://pytube.io/en/latest/index.html - sync docs
#async lib:
#python -m pip install git+https://github.com/msemple1111/pytube
#ПРИМЕЧАНИЕ:
#pytube async также упрощает конвейерную обработку,
#позволяя указывать функции обратного вызова для различных событий загрузки,
#таких как on progressили on complete.

def test():
    p = Playlist('https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e')
    # искаропки допускается ссылка с параметром видоса внутри!
    youtube_videos = []
    for url in p.video_urls:
        youtube_videos.append(url)
    return youtube_videos

if __name__ == '__main__':
    print(test())