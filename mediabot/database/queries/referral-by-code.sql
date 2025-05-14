SELECT
  "referral"."id",
  "referral"."code",
  COUNT("referral_click") AS "click_count",
  "referral"."created_at"
FROM
  "referral"
LEFT OUTER JOIN "referral_click" ON "referral_click"."referral_origin" = "referral"."id"
WHERE
  "referral"."instance_origin" = %(instance_origin)s AND "referral"."code" = %(code)s
GROUP BY "referral"."id";