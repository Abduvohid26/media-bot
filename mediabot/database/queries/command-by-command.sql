SELECT
  "command"."id" AS "command_id",
  "command"."command" AS "command_command",
  "command"."is_enabled" AS "command_is_enabled",
  "command"."created_at" AS "command_created_at",
  "message"."id" AS "command_message_id",
  "message"."message" AS "command_message_message",
  "message"."created_at" AS "command_message_created_at"
FROM "command"
LEFT OUTER JOIN "message"
  ON "command"."id" = "message"."command_origin"
WHERE
  "command"."instance_origin" = %(instance_origin)s
  AND "command"."command" = %(command)s;