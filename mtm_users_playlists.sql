--Многие--
CREATE TABLE IF NOT EXISTS users (
    tg_user_id TEXT NOT NULL UNIQUE
);
--Многие--
CREATE TABLE IF NOT EXISTS playlists (
    youtube_playlist_id TEXT NOT NULL UNIQUE
);
--Связующая--
CREATE TABLE IF NOT EXISTS users_playlists (
    tg_user_id TEXT NOT NULL,
    youtube_playlist_id TEXT NOT NULL,
    CONSTRAINT user_playlist PRIMARY KEY (tg_user_id, youtube_playlist_id)
    FOREIGN KEY (tg_user_id) REFERENCES users(tg_user_id)
    FOREIGN KEY (youtube_playlist_id) REFERENCES playlists(youtube_playlist_id)
);
