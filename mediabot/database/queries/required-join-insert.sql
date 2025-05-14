INSERT INTO "required_join" (instance_origin, target_chat) VALUES (%(instance_origin)s, %(target_chat)s) RETURNING "id";
