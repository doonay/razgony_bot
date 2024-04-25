--Многие--
CREATE TABLE IF NOT EXISTS playlists (
    youtube_playlist_id INTEGER NOT NULL UNIQUE,
    youtube_playlist_title TEXT NOT NULL,
    is_new INTEGER DEFAULT 1 NOT NULL
);
--Многие--
CREATE TABLE IF NOT EXISTS videos (
    youtube_video_id TEXT NOT NULL UNIQUE,
    youtube_video_title TEXT NOT NULL
);
--Связующая--
CREATE TABLE IF NOT EXISTS playlists_videos (
    youtube_playlist_id INTEGER NOT NULL,
    youtube_video_id TEXT NOT NULL,
    CONSTRAINT playlists_videos PRIMARY KEY (youtube_playlist_id, youtube_video_id)
    FOREIGN KEY (youtube_playlist_id) REFERENCES playlists(youtube_playlist_id)
    FOREIGN KEY (youtube_video_id) REFERENCES videos(youtube_video_id)
);
