SELECT
  DISTINCT "message"."message" AS "message_message",
  "message"."is_forward" AS "message_is_forward",
  "message"."created_at" AS "message_created_at"
FROM "message"
INNER JOIN "account"
  ON "account"."telegram_id" = %(account_id)s
LEFT OUTER JOIN "command"
  ON "command"."id" = "message"."command_origin"
WHERE
  "message"."instance_origin" = %(instance_origin)s
  AND COALESCE("message"."language_origin" = "account"."language_origin", "message"."language_origin" IS NULL)
  AND "command"."command" = %(command)s
  AND "command"."is_enabled"
ORDER BY "message"."created_at";