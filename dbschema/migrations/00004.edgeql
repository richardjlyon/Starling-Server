CREATE MIGRATION m1r3sxll6lh46j7wxn4gxwnouyjvlgearnwl4fbafl6zctahnvhcca
    ONTO m1plq6onrjlhvwhm2ogdvdreppggiz3xunc4glxjriiccrxgqdjjdq
{
  ALTER TYPE default::Bank {
      DROP PROPERTY auth_token_hash;
  };
};
