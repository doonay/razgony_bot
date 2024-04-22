CREATE TABLE IF NOT EXISTS youtube_video_urls (
    id integer PRIMARY KEY,
    youtube_video_url TEXT NOT NULL UNIQUE ON CONFLICT IGNORE,
    is_new INTEGER DEFAULT 1
);