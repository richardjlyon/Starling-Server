CREATE MIGRATION m1b2gf3xxerjzu5x6nodrhfusrdl6ykjmmjxiub5gkwgxfnizwcdba
    ONTO m1a5nhzzoxdytpuysrrbjuxxmyuix4ta2bw7qrg5pucbdtx3sljw7a
{
  ALTER TYPE default::Account {
      ALTER PROPERTY uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Transaction {
      ALTER PROPERTY uuid {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
