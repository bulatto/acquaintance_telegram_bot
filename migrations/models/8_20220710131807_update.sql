-- upgrade --
ALTER TABLE "adminuserid" ALTER COLUMN "user_id" TYPE BIGINT USING "user_id"::BIGINT;
ALTER TABLE "anonymousdialog" ALTER COLUMN "to_user_id" TYPE BIGINT USING "to_user_id"::BIGINT;
ALTER TABLE "anonymousdialog" ALTER COLUMN "user_id" TYPE BIGINT USING "user_id"::BIGINT;
ALTER TABLE "clickstats" ALTER COLUMN "user_id" TYPE BIGINT USING "user_id"::BIGINT;
ALTER TABLE "personinformation" ALTER COLUMN "user_id" TYPE BIGINT USING "user_id"::BIGINT;
ALTER TABLE "story" ALTER COLUMN "user_id" TYPE BIGINT USING "user_id"::BIGINT;
-- downgrade --
ALTER TABLE "story" ALTER COLUMN "user_id" TYPE INT USING "user_id"::INT;
ALTER TABLE "clickstats" ALTER COLUMN "user_id" TYPE INT USING "user_id"::INT;
ALTER TABLE "adminuserid" ALTER COLUMN "user_id" TYPE INT USING "user_id"::INT;
ALTER TABLE "anonymousdialog" ALTER COLUMN "to_user_id" TYPE INT USING "to_user_id"::INT;
ALTER TABLE "anonymousdialog" ALTER COLUMN "user_id" TYPE INT USING "user_id"::INT;
ALTER TABLE "personinformation" ALTER COLUMN "user_id" TYPE INT USING "user_id"::INT;
