CREATE MIGRATION m1qgn3mho7gfw5hr7eihjvfynxyyrh4yhweg7fj5az5l6gukjgla2q
    ONTO m1nt4wme7czzoa2gjiheweg6u7w66ux3c5redwdz2k3siqfnr7k57a
{
  CREATE TYPE default::NameDisplayname {
      CREATE PROPERTY display_name -> std::str;
      CREATE PROPERTY name -> std::str;
      CREATE PROPERTY name_fragment -> std::str;
  };
};
