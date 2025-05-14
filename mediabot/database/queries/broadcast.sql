SELECT 
  "broadcast"."id" AS "broadcast_id",
  "broadcast"."name" AS "broadcast_name",
  "broadcast"."is_running" AS "broadcast_is_running",
  "broadcast"."is_group" AS "broadcast_is_group",
  "broadcast"."is_silent" AS "broadcast_is_silent",
  "broadcast"."mps" AS "broadcast_mps",
  "broadcast"."jobs" AS "broadcast_jobs",
  "broadcast"."cursor" AS "broadcast_cursor",
  "broadcast"."eta" AS "broadcast_eta",
  "broadcast"."succeeded_jobs" AS "broadcast_succeeded_jobs",
  "broadcast"."failed_jobs" AS "broadcast_failed_jobs",
  "broadcast"."blocked_jobs" AS "broadcast_blocked_jobs",
  "broadcast"."created_at" AS "broadcast_created_at",

  "message"."id" AS "broadcast_message_id",
  "message"."message" AS "broadcast_message_message",

  "language"."id" AS "broadcast_message_language_id",
  "language"."name" AS "broadcast_message_language_name",
  "language"."code" AS "broadcast_message_language_code"
FROM "broadcast"
LEFT OUTER JOIN "message" ON "message"."id" = "broadcast"."message_origin"
LEFT OUTER JOIN "language" ON "message"."language_origin" = "language"."id"
WHERE "broadcast"."id" = %(broadcast_id)s
LIMIT 1;