INSERT INTO
  "account" (
    telegram_id,
    instance_origin,
    language_origin,
    referral_origin
  )
VALUES
  (
    %(telegram_id)s,
    %(instance_origin)s,
    COALESCE(
      (
        SELECT
          "id"
        FROM
          "language"
        WHERE
          "language"."code" = %(language_code)s
          AND "language"."instance_origin" = %(instance_origin)s
      )
    ), 
      (
        SELECT
          "id"
        FROM
          "referral"
        WHERE
          "referral"."code" = %(referral_code)s
          AND "referral"."instance_origin" = %(instance_origin)s
      )
  ) ON CONFLICT DO NOTHING RETURNING "id";
