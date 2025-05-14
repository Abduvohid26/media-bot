SELECT
  "command"."id" AS "command_id",
  "command"."command" AS "command_command",
  "command"."is_enabled" AS "command_is_enabled",
  "command"."created_at" AS "command_created_at",
  COUNT("message"."id") AS "command_message_count"
FROM "command"
LEFT OUTER JOIN "message"
  ON "command"."id" = "message"."command_origin"
WHERE
  "command"."id" = %(command_id)s
GROUP BY "command"."id";