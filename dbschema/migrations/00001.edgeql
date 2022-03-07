CREATE MIGRATION m1bomt5762cu2zobwwes6z3ulx6wmx55j6hcvgr526s25jwvdqy3pa
    ONTO initial
{
  CREATE TYPE default::Account {
      CREATE PROPERTY created_at -> std::datetime;
      CREATE REQUIRED PROPERTY currency -> std::str;
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY uuid -> std::uuid;
  };
  CREATE TYPE default::Transaction {
      CREATE REQUIRED PROPERTY amount -> std::float32;
      CREATE REQUIRED PROPERTY counterparty_name -> std::str;
      CREATE PROPERTY reference -> std::str;
      CREATE REQUIRED PROPERTY time -> std::datetime;
      CREATE REQUIRED PROPERTY uuid -> std::uuid;
  };
  ALTER TYPE default::Account {
      CREATE MULTI LINK transactions -> default::Transaction;
  };
  CREATE TYPE default::Bank {
      CREATE MULTI LINK accounts -> default::Account;
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY token -> std::str;
  };
  CREATE TYPE default::Category {
      CREATE MULTI LINK transactions -> default::Transaction;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::CategoryGroup {
      CREATE MULTI LINK subcategories -> default::Category;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  ALTER TYPE default::Category {
      CREATE REQUIRED LINK category -> default::CategoryGroup;
  };
  ALTER TYPE default::Transaction {
      CREATE LINK category -> default::Category;
  };
};
