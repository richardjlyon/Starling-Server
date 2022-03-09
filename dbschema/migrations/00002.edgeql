CREATE MIGRATION m1ff5ice3bfo2sryk3khv72flipugpvairdf4pco5n66h3ughoabbq
    ONTO m1vrt77zbn7eh642s2j4x7ubhexm4hbyiokiu4h7zftagq5tfhry2a
{
  ALTER TYPE default::Account {
      ALTER LINK transactions {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
