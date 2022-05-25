-- upgrade --
ALTER TABLE "personinformation" ALTER COLUMN "image_file_id" SET DEFAULT '';
-- downgrade --
ALTER TABLE "personinformation" ALTER COLUMN "image_file_id" DROP DEFAULT;
