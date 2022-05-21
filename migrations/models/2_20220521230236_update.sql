-- upgrade --
ALTER TABLE "personinformation" ALTER COLUMN "image_file_id" TYPE VARCHAR(200) USING "image_file_id"::VARCHAR(200);
-- downgrade --
ALTER TABLE "personinformation" ALTER COLUMN "image_file_id" TYPE VARCHAR(100) USING "image_file_id"::VARCHAR(100);
