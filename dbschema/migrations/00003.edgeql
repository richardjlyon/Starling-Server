CREATE MIGRATION m1nvjcl5r75ldtdbz6dglji563cdgnqotepeuj5wmm4kcjmnvv5otq
    ONTO m1o4jdgkjejum5pokm5aduapesgpzi7bydiuved7yxcrdstrse55wa
{
  ALTER TYPE default::Account {
      ALTER PROPERTY uuid {
          RENAME TO account_uuid;
      };
  };
};
