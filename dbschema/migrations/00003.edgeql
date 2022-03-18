CREATE MIGRATION m1abuuargkt2hsndn335sg5n4dw3qhllxvo4kz2aowsubjuptpdjma
    ONTO m1e7gipzw5jjry2uch6fkwqvuztk34jegfq2cdaryeitmi7537lctq
{
  ALTER TYPE default::Bank {
      CREATE MULTI LINK accounts := (.<bank[IS default::Account]);
  };
};
