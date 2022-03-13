CREATE MIGRATION m125de3zsfdxy3iayxmx3deg2iagjtweo34w7snzc2mq4vmjvg7l2a
    ONTO m1cs2eovfbwbwibqmswpujb2budjroudowivs3bfqwkefpce2fy6eq
{
  ALTER TYPE default::Account {
      CREATE PROPERTY server_last_updated -> std::datetime;
  };
};
