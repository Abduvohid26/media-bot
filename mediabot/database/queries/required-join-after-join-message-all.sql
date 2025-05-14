SELECT
  "message"."message",
  "message"."is_forward"
FROM "message"
LEFT OUTER JOIN "account"
  ON "account"."id" = %(account_origin)s
WHERE "required_join_origin" = %(required_join_origin)s
  AND "is_after_join" IS TRUE
  AND COALESCE("message"."language_origin" = "account"."language_origin", TRUE);
