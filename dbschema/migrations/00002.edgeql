CREATE MIGRATION m1o4jdgkjejum5pokm5aduapesgpzi7bydiuved7yxcrdstrse55wa
    ONTO m1byaenerq7fa77cxlm476mrpg4iyw7d7gzlwhk5phpelahnvcnyia
{
  ALTER TYPE default::Account {
      DROP PROPERTY bank_name;
  };
};
