UPDATE "account" SET "deleted_at" = CURRENT_TIMESTAMP WHERE "id" = %(account_id)s;
