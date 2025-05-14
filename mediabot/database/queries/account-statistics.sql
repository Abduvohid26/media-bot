SELECT
	"language"."name" AS "language_name",
	COUNT("account"."id") AS "account_count",
	COUNT("account"."id") FILTER(WHERE "account"."deleted_at" IS NOT NULL) AS "deleted_account_count",
	COUNT("account"."id") FILTER(WHERE "account"."created_at"::date = CURRENT_DATE) AS "today_new_account_count",
	COUNT("account"."id") FILTER(WHERE "account"."deleted_at"::date = CURRENT_DATE) AS "today_deleted_account_count"
FROM "language"
LEFT OUTER JOIN "account" ON "account"."language_origin" = "language"."id"
WHERE "language"."instance_origin" = %(instance_origin)s
GROUP BY "language"."id"

UNION

SELECT
	NULL AS "language_name",
	COUNT("account"."id") AS "account_count",
	COUNT("account"."id") FILTER(WHERE "account"."deleted_at" IS NOT NULL) AS "deleted_account_count",
	COUNT("account"."id") FILTER(WHERE "account"."created_at"::date = CURRENT_DATE) AS "today_new_account_count",
	COUNT("account"."id") FILTER(WHERE "account"."deleted_at"::date = CURRENT_DATE) AS "today_deleted_account_count"
FROM "account"
WHERE "account"."language_origin" IS NULL
	AND "account"."instance_origin" = %(instance_origin)s;
