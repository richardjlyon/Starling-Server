CREATE MIGRATION m1plq6onrjlhvwhm2ogdvdreppggiz3xunc4glxjriiccrxgqdjjdq
    ONTO m1qgn3mho7gfw5hr7eihjvfynxyyrh4yhweg7fj5az5l6gukjgla2q
{
  ALTER TYPE default::NameDisplayname {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
      ALTER PROPERTY name_fragment {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
