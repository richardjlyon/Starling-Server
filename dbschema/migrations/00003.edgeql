CREATE MIGRATION m1a5nhzzoxdytpuysrrbjuxxmyuix4ta2bw7qrg5pucbdtx3sljw7a
    ONTO m16pv4r7kj65gpenuep45bddhahclqql46eqdbuh5zfpid46743wca
{
  ALTER TYPE default::Bank {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
