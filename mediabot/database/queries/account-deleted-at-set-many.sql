UPDATE "account" SET "deleted_at" = %(deleted_at)s
FROM (SELECT UNNEST(ARRAY[{}])) AS "update_id"("id")
WHERE "account"."telegram_id" = "update_id"."id" AND "account"."instance_origin" = %(instance_origin)s;