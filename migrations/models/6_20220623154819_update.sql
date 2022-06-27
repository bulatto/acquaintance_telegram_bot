-- upgrade --
ALTER TABLE "adminuserid" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
CREATE TABLE IF NOT EXISTS "anonymousdialog" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL,
    "to_user_id" INT
);
COMMENT ON TABLE "anonymousdialog" IS 'Модель для хранения пользователей, ищущих диалог в анонимном чате.';;
ALTER TABLE "personinformation" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
-- downgrade --
ALTER TABLE "adminuserid" DROP COLUMN "updated_at";
ALTER TABLE "personinformation" DROP COLUMN "updated_at";
DROP TABLE IF EXISTS "anonymousdialog";
