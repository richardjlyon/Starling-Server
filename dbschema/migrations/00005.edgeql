CREATE MIGRATION m1cs2eovfbwbwibqmswpujb2budjroudowivs3bfqwkefpce2fy6eq
    ONTO m1hdars63vrng2qmtjbvllqs7ziocior2d72v7ilv2uglb4bm2zmrq
{
  ALTER TYPE default::Bank {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
