CREATE MIGRATION m1w65ghvwuv2m6ymk2imlzp74rxffwbqbq6ijtuppnsnvbhigp2fpa
    ONTO initial
{
  CREATE TYPE default::Bank {
      CREATE REQUIRED PROPERTY auth_token_hash -> std::str;
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Account {
      CREATE REQUIRED LINK bank -> default::Bank;
      CREATE PROPERTY created_at -> std::datetime;
      CREATE REQUIRED PROPERTY currency -> std::str;
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY uuid -> std::uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Transaction {
      CREATE REQUIRED LINK account -> default::Account {
          ON TARGET DELETE  DELETE SOURCE;
      };
      CREATE REQUIRED PROPERTY amount -> std::float32;
      CREATE REQUIRED PROPERTY counterparty_name -> std::str;
      CREATE PROPERTY reference -> std::str;
      CREATE REQUIRED PROPERTY time -> std::datetime;
      CREATE REQUIRED PROPERTY uuid -> std::uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Account {
      CREATE MULTI LINK transactions := (.<account[IS default::Transaction]);
  };
  CREATE TYPE default::Category {
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::CategoryGroup {
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Category {
      CREATE LINK category_group -> default::CategoryGroup;
  };
  ALTER TYPE default::CategoryGroup {
      CREATE MULTI LINK categories := (.<category_group[IS default::Category]);
  };
  ALTER TYPE default::Transaction {
      CREATE LINK category -> default::Category;
  };
  ALTER TYPE default::Category {
      CREATE MULTI LINK transactions := (.<category[IS default::Transaction]);
  };
};
