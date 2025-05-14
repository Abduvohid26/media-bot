SELECT
	"required_join"."id" AS "required_join_id",
	"required_join"."target_chat" AS "required_join_target_chat",
	"required_join"."join_link" AS "required_join_join_link",
	"message"."message" AS "required_join_message_message",
	COUNT("required_join_mark"."id" > 0) AS "required_join_has_mark",
	"required_join_mark"."has_joined" AS "required_join_mark_has_joined",
	"instance"."id" AS "instance_id"
FROM "required_join"
LEFT OUTER JOIN "required_join_mark"
	ON "required_join_mark"."required_join_origin" = "required_join"."id"
	AND "required_join_mark"."account_origin" = %(account_origin)s
LEFT OUTER JOIN "instance" ON "instance"."username" = "required_join"."target_chat"
LEFT OUTER JOIN "message"
	ON "message"."required_join_origin" = "required_join"."id"
		AND COALESCE("message"."language_origin" = %(account_language_origin)s, TRUE)
		AND "message"."is_after_join" IS FALSE
WHERE "required_join"."is_enabled" IS TRUE
  AND "required_join"."kind" = %(kind)s
  AND "required_join"."instance_origin" = %(instance_origin)s
GROUP BY "required_join"."id", "message"."message", "instance"."id", "required_join_mark"."id";