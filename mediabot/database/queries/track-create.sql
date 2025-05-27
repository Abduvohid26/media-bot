INSERT INTO tracks (query, video_id, title, performer, duration, thumbnail_url)
VALUES (:query, :video_id, :title, :performer, :duration, :thumbnail_url)
RETURNING id;
