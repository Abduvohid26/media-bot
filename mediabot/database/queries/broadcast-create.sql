WITH "inserted_message" AS (
  INSERT INTO "message" ("message", "language_origin", "instance_origin") VALUES (%(message)s, %(language_origin)s, %(instance_origin)s) RETURNING "id"
)
INSERT INTO "broadcast" ("name", "is_group", "is_silent", "jobs", "message_origin", "instance_origin")
SELECT %(name)s, %(is_group)s, %(is_silent)s, %(jobs)s, (SELECT "id" FROM "inserted_message" LIMIT 1), %(instance_origin)s
RETURNING "id";