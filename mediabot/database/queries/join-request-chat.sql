SELECT
  "join_request_chat"."id" AS "join_request_chat_id",
  "join_request_chat"."chat" AS "join_request_chat_chat",
  "join_request_chat"."created_at" AS "join_request_chat_created_at",
  "join_request_chat"."is_autoapprove" AS "join_request_chat_is_autoapprove",
  "join_request_chat"."is_autodecline" AS "join_request_chat_is_autodecline",
  "join_request_chat"."cursor" AS "join_request_chat_cursor",
  COUNT(DISTINCT "join_request"."id") AS "join_request_count",
  COUNT(DISTINCT "message"."id") AS "join_request_chat_message_count"
FROM "join_request_chat"
LEFT OUTER JOIN "join_request"
  ON "join_request"."join_request_chat_origin" = "join_request_chat"."id"
LEFT OUTER JOIN "message"
  ON "message"."join_request_chat_origin" = "join_request_chat"."id"
WHERE "join_request_chat"."id" = %(join_request_chat_id)s
GROUP BY "join_request_chat"."id"
LIMIT 1;