CREATE MIGRATION m1zzlgtunj7fl64ymmhfa5jxwnji3inffidmkra2fvoxjfa2omprua
    ONTO m1abuuargkt2hsndn335sg5n4dw3qhllxvo4kz2aowsubjuptpdjma
{
  CREATE TYPE default::Counterparty {
      CREATE PROPERTY display_name -> std::str;
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY uuid -> std::uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Transaction {
      CREATE REQUIRED LINK counterparty -> default::Counterparty {
          ON TARGET DELETE  DELETE SOURCE;
          SET REQUIRED USING (INSERT
              default::Counterparty
              {
                  name := 'DUMMY',
                  uuid := <std::uuid>'a6335e84-2872-4914-8c5d-3ed07d2a2f16'
              });
      };
  };
  ALTER TYPE default::Counterparty {
      CREATE MULTI LINK transactions := (.<counterparty[IS default::Transaction]);
  };
  ALTER TYPE default::Transaction {
      DROP PROPERTY counterparty_name;
  };
};
