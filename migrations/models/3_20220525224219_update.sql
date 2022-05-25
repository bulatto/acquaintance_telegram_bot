-- upgrade --
ALTER TABLE "personinformation" DROP COLUMN "image_path";
DROP TABLE IF EXISTS "personinformationview";
-- downgrade --
ALTER TABLE "personinformation" ADD "image_path" VARCHAR(200) NOT NULL;
