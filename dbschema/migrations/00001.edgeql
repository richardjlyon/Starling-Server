CREATE MIGRATION m1byaenerq7fa77cxlm476mrpg4iyw7d7gzlwhk5phpelahnvcnyia
    ONTO initial
{
  CREATE TYPE default::Account {
      CREATE REQUIRED PROPERTY account_name -> std::str;
      CREATE REQUIRED PROPERTY bank_name -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE PROPERTY created_at -> std::datetime;
      CREATE REQUIRED PROPERTY currency -> std::str;
      CREATE REQUIRED PROPERTY uuid -> std::uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Bank {
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  ALTER TYPE default::Account {
      CREATE REQUIRED LINK bank -> default::Bank;
  };
  ALTER TYPE default::Bank {
      CREATE MULTI LINK accounts := (.<bank[IS default::Account]);
  };
  CREATE TYPE default::Transaction {
      CREATE REQUIRED LINK account -> default::Account;
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
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  ALTER TYPE default::Transaction {
      CREATE LINK category -> default::Category;
  };
  ALTER TYPE default::Category {
      CREATE MULTI LINK transactions := (.<category[IS default::Transaction]);
  };
  CREATE TYPE default::CategoryGroup {
      CREATE MULTI LINK categories -> default::Category {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY name -> std::str;
  };
};
