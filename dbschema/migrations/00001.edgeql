CREATE MIGRATION m15hi4lqboaqvz27czzp5b6frncoq34gszprq4d5rwi7ihliisp3fq
    ONTO initial
{
  CREATE TYPE default::Account {
      CREATE REQUIRED PROPERTY account_name -> std::str;
      CREATE REQUIRED PROPERTY bank_name -> std::str;
      CREATE PROPERTY created_at -> std::datetime;
      CREATE REQUIRED PROPERTY currency -> std::str;
      CREATE REQUIRED PROPERTY uuid -> std::uuid {
          CREATE CONSTRAINT std::exclusive;
      };
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
      CREATE MULTI LINK transactions -> default::Transaction;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::CategoryGroup {
      CREATE MULTI LINK categories -> default::Category;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  ALTER TYPE default::Transaction {
      CREATE LINK category -> default::Category;
  };
};
