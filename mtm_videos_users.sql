--Многие--
CREATE TABLE IF NOT EXISTS videos (
    youtube_video_id TEXT NOT NULL UNIQUE,
    youtube_video_title TEXT NOT NULL UNIQUE,
    is_new INTEGER DEFAULT 1 NOT NULL
);
--Многие--
CREATE TABLE IF NOT EXISTS users (
    tg_user_id INTEGER NOT NULL UNIQUE
);
--Связующая--
CREATE TABLE IF NOT EXISTS videos_users (
    youtube_video_id TEXT NOT NULL,
    tg_user_id INTEGER NOT NULL,
    CONSTRAINT videos_users PRIMARY KEY (youtube_video_id, tg_user_id)
    FOREIGN KEY (youtube_video_id) REFERENCES videos(youtube_video_id)
    FOREIGN KEY (tg_user_id) REFERENCES users(tg_user_id)
);
