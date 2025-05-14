SELECT "id", "group_id" FROM "group" WHERE "instance_origin" = %(instance_origin)s AND "id" > %(cursor)s AND "deleted_at" IS NULL ORDER BY "id" LIMIT %(limit)s;
