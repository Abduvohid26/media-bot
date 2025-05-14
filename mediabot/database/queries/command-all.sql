SELECT
  "command"."id" AS "command_id",
  "command"."command" AS "command_command",
  "command"."is_enabled" AS "command_is_enabled",
  "command"."created_at" AS "command_created_at",
  COUNT("message") AS "command_message_count"
FROM
  "command"
LEFT OUTER JOIN "message"
  ON "message"."command_origin" = "command"."id"
WHERE
  "command"."instance_origin" = %(instance_origin)s
GROUP BY
  "command"."id"
ORDER BY
  "command"."is_enabled"
OFFSET %(offset)s
LIMIT %(limit)s;