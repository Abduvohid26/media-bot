SELECT
  "join_request_chat"."id" AS "join_request_chat_id",
  "join_request_chat"."is_autoapprove" AS "join_request_chat_is_autoapprove",
  "join_request_chat"."is_autodecline" AS "join_request_chat_is_autodecline",
  "message"."message" AS "join_request_chat_message"
FROM "join_request_chat"
LEFT OUTER JOIN "join_request"
  ON "join_request"."join_request_chat_origin" = "join_request_chat"."id"
LEFT OUTER JOIN "language"
  ON COALESCE(LOWER("language"."code") = LOWER(%(language_code)s), FALSE)
LEFT OUTER JOIN "message"
  ON "message"."join_request_chat_origin" = "join_request_chat"."id"
  AND COALESCE("message"."language_origin" = "language"."id", "message"."language_origin" IS NULL)
WHERE "join_request_chat"."instance_origin" = %(instance_origin)s AND "join_request_chat"."chat" = %(join_request_chat)s
GROUP BY "join_request_chat"."id", "message"."id"
LIMIT 1;
