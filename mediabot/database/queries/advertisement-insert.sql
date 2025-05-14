INSERT INTO "advertisement" (instance_origin, name, kind) VALUES (%(instance_origin)s, %(name)s, %(kind)s) RETURNING "id";
