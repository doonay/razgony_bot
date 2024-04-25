--Многие--
CREATE TABLE IF NOT EXISTS playlists (
    youtube_playlist_id integer NOT NULL UNIQUE,
    is_new INTEGER DEFAULT 1 NOT NULL
);
--Многие--
CREATE TABLE IF NOT EXISTS videos (
    youtube_video_id text NOT NULL UNIQUE
);
--Связующая--
CREATE TABLE IF NOT EXISTS playlists_videos (
    youtube_playlist_id integer NOT NULL,
    youtube_video_id text NOT NULL,
    CONSTRAINT playlists_videos PRIMARY KEY (youtube_playlist_id, youtube_video_id)
    FOREIGN KEY (youtube_playlist_id) REFERENCES playlists(youtube_playlist_id)
    FOREIGN KEY (youtube_video_id) REFERENCES videos(youtube_video_id)
);
