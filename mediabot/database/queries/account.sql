SELECT
  "account"."id",
  "account"."telegram_id",
  "account"."is_admin",
  "account"."created_at",
  "language"."id" AS "language_id",
  "language"."code" AS "language_code",
  "language"."name" AS "language_name",

  "referral"."id" AS "referral_id",
  "referral"."code" AS "referral_code",
  "referral"."created_at" AS "referral_created_at"
FROM "account"
  LEFT OUTER JOIN "language" ON "language"."id" = "account"."language_origin"
  LEFT OUTER JOIN "referral" ON "referral"."id" = "account"."referral_origin"
WHERE
  "account"."instance_origin" = %(instance_origin)s
  AND "account"."telegram_id" = %(account_telegram_id)s;