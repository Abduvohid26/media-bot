SELECT
	"referral"."id" AS "referral_id",
	"referral"."code" AS "referral_code",
	"referral"."created_at" AS "referral_created_at",
	"account_new_language"."name" AS "account_new_language_name",
	COUNT(DISTINCT "account_new"."id") AS "account_new_count",
	"account_click_language"."name" AS "account_click_language_name",
	COUNT(DISTINCT "account_click"."id") AS "account_click_count"
FROM "referral"
LEFT OUTER JOIN "referral_click" ON "referral_click"."referral_origin" = "referral"."id"
LEFT OUTER JOIN "account" AS "account_new" ON "account_new"."referral_origin" = "referral"."id"
LEFT OUTER JOIN "language" AS "account_new_language" ON "account_new_language"."id" = "account_new"."language_origin"
LEFT OUTER JOIN "account" AS "account_click" ON "account_click"."referral_origin" = "referral"."id" AND "account_click"."id" = "referral_click"."account_origin"
LEFT OUTER JOIN "language" AS "account_click_language" ON "account_click_language"."id" = "account_new"."language_origin"
WHERE "referral"."id" = %(referral_id)s
GROUP BY "referral"."id", "account_new_language"."name", "account_click_language"."name";