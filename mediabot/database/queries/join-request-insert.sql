INSERT INTO "join_request" (user_id, join_request_chat_origin, instance_origin) VALUES (%(user_id)s, %(join_request_chat_origin)s, %(instance_origin)s) ON CONFLICT DO NOTHING;
