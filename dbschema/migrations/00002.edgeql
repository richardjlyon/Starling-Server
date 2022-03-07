CREATE MIGRATION m16pv4r7kj65gpenuep45bddhahclqql46eqdbuh5zfpid46743wca
    ONTO m1bomt5762cu2zobwwes6z3ulx6wmx55j6hcvgr526s25jwvdqy3pa
{
  ALTER TYPE default::Bank {
      DROP PROPERTY token;
  };
};
