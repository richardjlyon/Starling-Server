CREATE MIGRATION m12jrwc33eyrdrnqqmuqe3gw6tygwrn5tgdijrqfm5zezqag7gp3ca
    ONTO m1f73vi5soy6tpnxf5gu44g7vatrak22dxudsxakudgobshvt5nbmq
{
  CREATE TYPE default::CategoryMap {
      CREATE LINK category -> default::Category;
      CREATE PROPERTY displayname -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Counterparty {
      DROP PROPERTY displayname;
  };
  ALTER TYPE default::DisplayNameMap RENAME TO default::DisplaynameMap;
  ALTER TYPE default::DisplaynameMap {
      ALTER PROPERTY fragment {
          RENAME TO name;
      };
  };
};
