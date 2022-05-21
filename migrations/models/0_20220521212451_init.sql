-- upgrade --
CREATE TABLE IF NOT EXISTS "personinformation" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" VARCHAR(4096) NOT NULL,
    "image_path" VARCHAR(200) NOT NULL,
    "is_published" BOOL NOT NULL  DEFAULT False
);
COMMENT ON TABLE "personinformation" IS 'Модель для хранения анкеты';
CREATE TABLE IF NOT EXISTS "personinformationview" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "telegram_nickname" VARCHAR(100) NOT NULL,
    "story_id" INT NOT NULL REFERENCES "personinformation" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "personinformationview" IS 'Модель для хранения просмотров историй';
CREATE TABLE IF NOT EXISTS "story" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" VARCHAR(4096) NOT NULL,
    "is_published" BOOL NOT NULL  DEFAULT False
);
COMMENT ON TABLE "story" IS 'Модель для хранения историй';
CREATE TABLE IF NOT EXISTS "storyview" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "telegram_nickname" VARCHAR(100) NOT NULL,
    "story_id" INT NOT NULL REFERENCES "story" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "storyview" IS 'Модель для хранения просмотров историй';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
