-- upgrade --
ALTER TABLE "adminuserid" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
ALTER TABLE "anonymousdialog" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS "clickstats" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL,
    "button" INT NOT NULL
);
COMMENT ON TABLE "clickstats" IS 'Модель для хранения статистики нажатий на кнопки бота.';;
ALTER TABLE "personinformation" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "adminuserid" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
ALTER TABLE "anonymousdialog" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
ALTER TABLE "personinformation" ALTER COLUMN "updated_at" TYPE TIMESTAMPTZ USING "updated_at"::TIMESTAMPTZ;
DROP TABLE IF EXISTS "clickstats";
