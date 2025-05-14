UPDATE "group" SET "deleted_at" = %(deleted_at)s
FROM (SELECT UNNEST(ARRAY[{}])) AS "update_id"("id")
WHERE "group"."group_id" = "update_id"."id" AND "group"."instance_origin" = %(instance_origin)s;
