SELECT
  "message"."id" AS "message_id",
  "message"."message" AS "message_message",
  "message"."is_attach" AS "message_is_attach",
  "message"."is_forward" AS "message_is_forward",
  "message"."is_after_join" AS "message_is_after_join",
  "message"."created_at" AS "message_created_at",
  "language"."id" AS "message_language_id",
  "language"."code" AS "message_language_code",
  "language"."name" AS "message_language_name"
FROM
  "message"
LEFT OUTER JOIN "language"
  ON "language"."id" = "message"."language_origin"
GROUP BY
  "message"."id", "language"."id"
HAVING
  COALESCE("command_origin" = %(command_origin)s, FALSE)
  OR COALESCE("required_join_origin" = %(required_join_origin)s, FALSE)
  OR COALESCE("join_request_chat_origin" = %(join_request_chat_origin)s, FALSE)
  OR COALESCE("advertisement_origin" = %(advertisement_origin)s, FALSE)
ORDER BY "message"."created_at" DESC;