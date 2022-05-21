-- upgrade --
ALTER TABLE "personinformation" ADD "image_file_id" VARCHAR(100) NOT NULL;
-- downgrade --
ALTER TABLE "personinformation" DROP COLUMN "image_file_id";
