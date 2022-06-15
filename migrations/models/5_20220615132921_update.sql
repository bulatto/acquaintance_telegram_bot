-- upgrade --
CREATE TABLE IF NOT EXISTS "adminuserid" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(32) NOT NULL,
    "user_id" INT NOT NULL
);
COMMENT ON TABLE "adminuserid" IS 'Модель для хранения связи админских логинов и его user_id, для возможности';
-- downgrade --
DROP TABLE IF EXISTS "adminuserid";
