CREATE MIGRATION m1m33getabs37evegdzzy6d3fwtihd3s6bppmgrzsfhkosydejgqqq
    ONTO m1b2gf3xxerjzu5x6nodrhfusrdl6ykjmmjxiub5gkwgxfnizwcdba
{
  ALTER TYPE default::Category {
      DROP LINK category;
  };
  ALTER TYPE default::CategoryGroup {
      ALTER LINK subcategories {
          RENAME TO categories;
      };
  };
};
