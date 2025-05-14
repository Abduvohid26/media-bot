SELECT
	COUNT(*) AS "group_count",
	COUNT("group"."id") FILTER (WHERE "group"."deleted_at" IS NOT NULL) AS "deleted_group_count",
	COUNT("group"."id") FILTER (WHERE "group"."created_at"::date = CURRENT_DATE) AS "today_new_group_count",
	COUNT("group"."id") FILTER (WHERE "group"."deleted_at"::date = CURRENT_DATE) AS "today_deleted_group_count"
FROM "group"
WHERE "group"."instance_origin" = %(instance_origin)s;