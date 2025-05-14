SELECT
  "advertisement"."id" AS "advertisement_id",
  "advertisement"."name" AS "advertisement_name",
  "advertisement"."kind" AS "advertisement_kind",
  "advertisement"."is_enabled" AS "advertisement_is_enabled",
  "advertisement"."created_at" AS "advertisement_created_at",
  COUNT(DISTINCT "message"."id") AS "advertisement_message_count",
  COUNT(DISTINCT "message_seen"."id") AS "advertisement_message_seen_count"
FROM "advertisement"
LEFT OUTER JOIN "message"
  ON "message"."advertisement_origin" = "advertisement"."id"
LEFT OUTER JOIN "message_seen"
  ON "message_seen"."message_origin" = "message"."id"
WHERE "advertisement"."id" = %(advertisement_id)s
GROUP BY "advertisement"."id";