SELECT
  "required_join"."id",
  "required_join"."kind"
FROM
  "required_join"
LEFT OUTER JOIN "required_join_mark"
  ON "required_join_mark"."required_join_origin" = "required_join"."id"
  AND "required_join_mark"."account_origin" = %(account_origin)s
WHERE
  "required_join"."is_enabled" IS TRUE
  AND "required_join"."instance_origin" = %(instance_origin)s
  AND "required_join"."target_chat" = %(target_chat)s OR "required_join"."target_chat" = %(target_chat_id)s::text
GROUP BY "required_join"."id", "required_join_mark"."id"
HAVING "required_join_mark"."id" IS NOT NULL;