SELECT
  "message"."id",
  "message"."message",
  "message"."is_attach",
  "message"."is_onetime",
  "message"."is_forward",
  (COUNT("message_seen"."id") > 0) AS "is_seen"
FROM "message"
  LEFT OUTER JOIN "advertisement" ON "advertisement"."id" = "message"."advertisement_origin"
  LEFT OUTER JOIN "language" ON "language"."id" = "message"."language_origin"
  LEFT OUTER JOIN "account" ON "account"."id" = %(account_origin)s AND "account"."instance_origin" = %(instance_origin)s
  LEFT OUTER JOIN "message_seen" ON "message_seen"."message_origin" = "message"."id" AND "message_seen"."account_origin" = "account"."id"
WHERE
  "message"."instance_origin" = %(instance_origin)s
  AND "advertisement"."is_enabled" IS TRUE
  AND (CASE WHEN "advertisement"."kind" IS NULL THEN TRUE ELSE "advertisement"."kind" = %(kind)s END)
  AND COALESCE("account"."language_origin" = "message"."language_origin", TRUE)
GROUP BY "message"."id";