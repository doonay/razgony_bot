INSERT OR IGNORE INTO users (tg_user_id) VALUES ({tg_user_id});
INSERT OR IGNORE INTO playlists (youtube_playlist_id) VALUES ('{youtube_playlist_id}');
INSERT OR IGNORE INTO users_playlists (tg_user_id, youtube_playlist_id) VALUES ({tg_user_id}, '{youtube_playlist_id}');