CREATE MIGRATION m1e7gipzw5jjry2uch6fkwqvuztk34jegfq2cdaryeitmi7537lctq
    ONTO m1w65ghvwuv2m6ymk2imlzp74rxffwbqbq6ijtuppnsnvbhigp2fpa
{
  ALTER TYPE default::Account {
      ALTER LINK bank {
          ON TARGET DELETE  DELETE SOURCE;
      };
  };
};
