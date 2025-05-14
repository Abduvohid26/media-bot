SELECT
  "required_join"."id",
  "required_join"."kind",
  "required_join"."target_chat",
  "required_join"."join_link",
  "required_join"."target_join_count",
  "required_join"."is_enabled",
  "required_join"."is_optional",
  "required_join"."target_end_time",
  "required_join"."created_at",
  COUNT(DISTINCT "message"."id") AS "message_count",
  COUNT(DISTINCT "required_join_mark"."id") AS "required_join_mark_count",
  COUNT(DISTINCT "required_join_mark"."id") FILTER(WHERE "required_join_mark"."has_joined" IS TRUE) AS "required_join_mark_has_joined_count"
FROM "required_join"
LEFT OUTER JOIN "required_join_mark" ON "required_join_mark"."required_join_origin" = "required_join"."id"
LEFT OUTER JOIN "message" ON "message"."required_join_origin" = "required_join"."id"
WHERE "required_join"."id" = %(required_join_id)s
GROUP BY "required_join"."id";