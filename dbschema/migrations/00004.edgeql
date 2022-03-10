CREATE MIGRATION m1hdars63vrng2qmtjbvllqs7ziocior2d72v7ilv2uglb4bm2zmrq
    ONTO m1nvjcl5r75ldtdbz6dglji563cdgnqotepeuj5wmm4kcjmnvv5otq
{
  ALTER TYPE default::Account {
      ALTER PROPERTY account_name {
          RENAME TO name;
      };
  };
  ALTER TYPE default::Account {
      ALTER PROPERTY account_uuid {
          RENAME TO uuid;
      };
  };
};
